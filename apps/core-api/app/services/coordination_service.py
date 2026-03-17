"""Platform coordination layer — orchestrates A2A agent collaboration.

This is NOT an independent service. It's a responsibility layer within core-api
that coordinates delegations to specialized agents and writes results back.

Horizon 2: supports both in-process agents and external HTTP agents.
External agents are reached via HTTP POST; results always flow back here.
"""

import logging
import os
import time
import uuid
from collections.abc import Callable, Coroutine

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.a2a_protocol import AgentResult, DelegationContract, TaskEnvelope
from app.services.agents.github_signal_agent import run_github_signal_agent
from app.services.agents.matching_agent import run_matching_agent
from app.services.agents.review_prep_agent import run_review_prep_agent
from app.services.agents.vc_agent import run_vc_agent
from app.services.event_write_service import EventWriteService

logger = logging.getLogger(__name__)

# Type alias for in-process agent functions
AgentFn = Callable[[TaskEnvelope, DelegationContract], Coroutine[None, None, AgentResult]]

# External agent endpoint overrides (env-based)
# If set, the agent is called via HTTP instead of in-process.
EXTERNAL_AGENT_URLS: dict[str, str] = {}
EXTERNAL_AGENT_TOKENS: dict[str, str] = {}

_github_signal_url = os.getenv("GITHUB_SIGNAL_AGENT_URL")
if _github_signal_url:
    EXTERNAL_AGENT_URLS["github_signal_agent"] = _github_signal_url
    _token = os.getenv("GITHUB_SIGNAL_AGENT_TOKEN", "")
    if _token:
        EXTERNAL_AGENT_TOKENS["github_signal_agent"] = _token

_vc_agent_url = os.getenv("VC_AGENT_URL")
if _vc_agent_url:
    EXTERNAL_AGENT_URLS["vc_agent"] = _vc_agent_url
    _vc_token = os.getenv("VC_AGENT_TOKEN", "")
    if _vc_token:
        EXTERNAL_AGENT_TOKENS["vc_agent"] = _vc_token

# In-process agent registry
IN_PROCESS_AGENTS: dict[str, AgentFn] = {
    "matching_agent": run_matching_agent,
    "review_prep_agent": run_review_prep_agent,
    "github_signal_agent": run_github_signal_agent,
    "vc_agent": run_vc_agent,
}


class CoordinationService:
    """Coordinates agent delegations and writes results back to platform."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._event_svc = EventWriteService(session)

    async def delegate_matching(self, envelope: TaskEnvelope) -> AgentResult:
        """Delegate to matching agent and record result."""
        contract = DelegationContract(
            envelope_id=envelope.envelope_id,
            delegator_agent="platform_coordinator",
            delegatee_agent="matching_agent",
            delegation_type="matching",
            requested_output="collaboration_suggestions",
        )

        result = await self._execute_delegation(contract, envelope)
        await self._record_delegation(contract, result)
        return result

    async def delegate_review_prep(self, envelope: TaskEnvelope) -> AgentResult:
        """Delegate to review prep agent and record result."""
        contract = DelegationContract(
            envelope_id=envelope.envelope_id,
            delegator_agent="platform_coordinator",
            delegatee_agent="review_prep_agent",
            delegation_type="review_prep",
            requested_output="evidence_review_brief",
        )

        result = await self._execute_delegation(contract, envelope)
        await self._record_delegation(contract, result)
        return result

    async def delegate_github_signal(self, envelope: TaskEnvelope) -> AgentResult:
        """Delegate to GitHub signal agent and record result."""
        contract = DelegationContract(
            envelope_id=envelope.envelope_id,
            delegator_agent="platform_coordinator",
            delegatee_agent="github_signal_agent",
            delegation_type="github_signal",
            requested_output="signal_snapshot",
        )
        result = await self._execute_delegation(contract, envelope)
        await self._record_delegation(contract, result)
        return result

    async def delegate_vc_issuance(self, envelope: TaskEnvelope) -> AgentResult:
        """Delegate to VC agent and record result."""
        contract = DelegationContract(
            envelope_id=envelope.envelope_id,
            delegator_agent="platform_coordinator",
            delegatee_agent="vc_agent",
            delegation_type="vc_issuance",
            requested_output="vc_recommendation",
            human_checkpoint_required=True,
        )
        result = await self._execute_delegation(contract, envelope)
        await self._record_delegation(contract, result)
        return result

    async def _execute_delegation(
        self,
        contract: DelegationContract,
        envelope: TaskEnvelope,
    ) -> AgentResult:
        """Execute a delegation via in-process call or external HTTP."""
        contract.status = "in_progress"
        agent_name = contract.delegatee_agent
        is_external = agent_name in EXTERNAL_AGENT_URLS
        start = time.monotonic()
        fallback_used = False

        try:
            if is_external:
                result = await self._call_external_agent(
                    EXTERNAL_AGENT_URLS[agent_name], envelope, contract
                )
            elif agent_name in IN_PROCESS_AGENTS:
                result = await IN_PROCESS_AGENTS[agent_name](envelope, contract)
            else:
                raise ValueError(f"Unknown agent: {agent_name}")

            result.trace_id = envelope.trace_id
            contract.status = "completed"
            latency_ms = int((time.monotonic() - start) * 1000)

            from app.metrics import metrics

            metrics.inc("delegation_total", agent=agent_name, status="success")
            metrics.timing("delegation_latency_ms", latency_ms, agent=agent_name)

            logger.info(
                "delegation_completed",
                extra={
                    "event_type": "delegation_completed",
                    "delegation_id": contract.delegation_id,
                    "delegatee_agent": agent_name,
                    "delegation_type": contract.delegation_type,
                    "result_type": result.result_type,
                    "confidence": result.confidence,
                    "trace_id": envelope.trace_id,
                    "correlation_id": contract.correlation_id,
                    "task_id": envelope.task_id,
                    "external": is_external,
                    "fallback_used": False,
                    "latency_ms": latency_ms,
                    "result_status": "success",
                },
            )
            return result

        except Exception:
            logger.exception(
                "Delegation %s failed (agent=%s)",
                contract.delegation_id,
                agent_name,
            )
            contract.status = "failed"

            # If external agent failed, try in-process fallback
            if is_external and agent_name in IN_PROCESS_AGENTS:
                fallback_used = True
                logger.info(
                    "delegation_fallback",
                    extra={
                        "event_type": "delegation_fallback",
                        "delegation_id": contract.delegation_id,
                        "delegatee_agent": agent_name,
                        "trace_id": envelope.trace_id,
                        "fallback_reason": "external_agent_failed",
                    },
                )
                try:
                    result = await IN_PROCESS_AGENTS[agent_name](envelope, contract)
                    result.trace_id = envelope.trace_id
                    contract.status = "completed"
                    latency_ms = int((time.monotonic() - start) * 1000)
                    logger.info(
                        "delegation_completed",
                        extra={
                            "event_type": "delegation_completed",
                            "delegation_id": contract.delegation_id,
                            "delegatee_agent": agent_name,
                            "trace_id": envelope.trace_id,
                            "fallback_used": True,
                            "latency_ms": latency_ms,
                            "result_status": "success_via_fallback",
                        },
                    )
                    return result
                except Exception:
                    logger.exception(
                        "In-process fallback also failed for %s",
                        agent_name,
                    )

            latency_ms = int((time.monotonic() - start) * 1000)
            metrics.inc("delegation_total", agent=agent_name, status="failed")
            if fallback_used:
                metrics.inc("delegation_fallback_total", agent=agent_name)

            logger.info(
                "delegation_failed",
                extra={
                    "event_type": "delegation_failed",
                    "delegation_id": contract.delegation_id,
                    "delegatee_agent": agent_name,
                    "trace_id": envelope.trace_id,
                    "fallback_used": fallback_used,
                    "latency_ms": latency_ms,
                    "result_status": "failed",
                    "error_code": "delegation_failed",
                },
            )
            return AgentResult(
                delegation_id=contract.delegation_id,
                result_type="error",
                summary="Agent delegation failed. Please try again or contact support.",
                confidence=0.0,
                requires_human_review=True,
                trace_id=envelope.trace_id,
                error_code="delegation_failed",
            )

    async def _call_external_agent(
        self,
        url: str,
        envelope: TaskEnvelope,
        contract: DelegationContract,
    ) -> AgentResult:
        """Call an external agent via HTTP POST."""
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "X-Trace-Id": envelope.trace_id,
            "X-Delegation-Id": contract.delegation_id,
        }
        agent_token = EXTERNAL_AGENT_TOKENS.get(contract.delegatee_agent, "")
        if agent_token:
            headers["Authorization"] = f"Bearer {agent_token}"

        async with httpx.AsyncClient(timeout=contract.timeout_seconds) as client:
            response = await client.post(
                url,
                json={
                    "envelope": envelope.model_dump(),
                    "contract": contract.model_dump(),
                },
                headers=headers,
            )
            response.raise_for_status()
            return AgentResult.model_validate(response.json())

    async def _record_delegation(self, contract: DelegationContract, result: AgentResult) -> None:
        """Record delegation and result as a domain event."""
        delegation_uuid = uuid.UUID(contract.delegation_id)
        await self._event_svc.record_domain_event(
            event_type="a2a_delegation_completed",
            aggregate_type="delegation",
            aggregate_id=delegation_uuid,
            payload={
                "delegation_id": contract.delegation_id,
                "envelope_id": contract.envelope_id,
                "delegatee_agent": contract.delegatee_agent,
                "delegation_type": contract.delegation_type,
                "status": contract.status,
                "result_type": result.result_type,
                "summary": result.summary[:500],
                "confidence": result.confidence,
                "requires_human_review": result.requires_human_review,
                "trace_id": result.trace_id,
                "correlation_id": contract.correlation_id,
            },
            source_channel="a2a",
        )
