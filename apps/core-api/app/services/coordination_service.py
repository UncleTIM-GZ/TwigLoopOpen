"""Platform coordination layer — orchestrates A2A agent collaboration.

This is NOT an independent service. It's a responsibility layer within core-api
that coordinates delegations to specialized agents and writes results back.

Phase 4 minimum: agents are in-process functions, not external services.
Future: agents become external A2A endpoints.
"""

import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.a2a_protocol import AgentResult, DelegationContract, TaskEnvelope
from app.services.agents.github_signal_agent import run_github_signal_agent
from app.services.agents.matching_agent import run_matching_agent
from app.services.agents.review_prep_agent import run_review_prep_agent
from app.services.agents.vc_agent import run_vc_agent
from app.services.event_write_service import EventWriteService

logger = logging.getLogger(__name__)


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

        result = await self._execute_delegation(contract, envelope, run_matching_agent)
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

        result = await self._execute_delegation(contract, envelope, run_review_prep_agent)
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
        result = await self._execute_delegation(contract, envelope, run_github_signal_agent)
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
        result = await self._execute_delegation(contract, envelope, run_vc_agent)
        await self._record_delegation(contract, result)
        return result

    async def _execute_delegation(
        self,
        contract: DelegationContract,
        envelope: TaskEnvelope,
        agent_fn: Any,
    ) -> AgentResult:
        """Execute a delegation by calling the agent function."""
        contract.status = "in_progress"
        try:
            result = await agent_fn(envelope, contract)
            contract.status = "completed"
            return result
        except Exception as exc:
            logger.exception("Delegation %s failed", contract.delegation_id)
            contract.status = "failed"
            return AgentResult(
                delegation_id=contract.delegation_id,
                result_type="error",
                summary=f"Agent failed: {exc}",
                confidence=0.0,
                requires_human_review=True,
            )

    async def _record_delegation(self, contract: DelegationContract, result: AgentResult) -> None:
        """Record delegation and result as a domain event."""
        delegation_uuid = (
            uuid.UUID(contract.delegation_id) if len(contract.delegation_id) == 36 else uuid.uuid4()
        )
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
            },
            source_channel="a2a",
        )
