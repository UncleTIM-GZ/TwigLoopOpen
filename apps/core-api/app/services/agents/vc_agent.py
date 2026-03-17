"""VC Agent — checks issuance eligibility and produces recommendation.

H2.1: supports lifecycle_action context for issuance and revoke_check.
Does NOT issue VC directly — returns recommendation for platform to execute.
"""

from app.domain.a2a_protocol import AgentResult, DelegationContract, TaskEnvelope

AGENT_VERSION = "2.0.0"


async def run_vc_agent(envelope: TaskEnvelope, contract: DelegationContract) -> AgentResult:
    """Check VC issuance eligibility and produce recommendation."""
    task_status = envelope.current_status
    verification_status = envelope.signal_context.get("verification_status", "unverified")
    completion_mode = envelope.signal_context.get("completion_mode", "evidence_backed")
    evidence_count = envelope.signal_context.get("evidence_count", 0)
    try:
        ewu = float(envelope.constraints.get("ewu", 0))
    except (ValueError, TypeError):
        ewu = 0.0
    actor_id = envelope.signal_context.get("target_actor_id", "")

    # H2.1: lifecycle context
    credential_id = envelope.signal_context.get("credential_id", "")
    lifecycle_action = envelope.signal_context.get("lifecycle_action", "issuance")

    reasons: list[str] = []
    eligible = True

    if lifecycle_action == "issuance":
        eligible, reasons = _check_issuance_eligibility(
            task_status, verification_status, completion_mode, evidence_count
        )
    elif lifecycle_action == "revoke_check":
        eligible = True
        reasons = ["Revocation is a platform decision — agent acknowledges request"]

    if lifecycle_action == "issuance":
        if eligible:
            decision = "recommend_issue"
            summary = f"VC issuance recommended for task (EWU: {ewu}). All gates passed."
            basis = "verified" if completion_mode == "evidence_backed" else "legacy"
        else:
            decision = "deny"
            summary = f"VC issuance denied: {'; '.join(reasons)}"
            basis = "none"
    else:
        decision = "acknowledge"
        summary = f"Lifecycle action '{lifecycle_action}' acknowledged"
        basis = "platform_decision"

    return AgentResult(
        delegation_id=contract.delegation_id,
        result_type="vc_recommendation",
        summary=summary,
        structured_payload={
            "issuance_decision": decision,
            "issuance_basis": basis,
            "task_status": task_status,
            "verification_status": verification_status,
            "completion_mode": completion_mode,
            "evidence_count": evidence_count,
            "ewu": ewu,
            "target_actor_id": actor_id,
            "reasons": reasons,
            "lifecycle_action": lifecycle_action,
            "credential_id": credential_id,
        },
        confidence=0.95 if eligible else 0.9,
        requires_human_review=True,
        agent_version=AGENT_VERSION,
        trace_id=envelope.trace_id,
    )


def _check_issuance_eligibility(
    task_status: str,
    verification_status: str,
    completion_mode: str,
    evidence_count: int,
) -> tuple[bool, list[str]]:
    """Check issuance eligibility gates."""
    reasons: list[str] = []
    eligible = True

    if task_status != "completed":
        eligible = False
        reasons.append(f"Task not completed (current: {task_status})")

    if completion_mode == "evidence_backed" and verification_status != "verified":
        eligible = False
        reasons.append(f"Verification required but status is: {verification_status}")

    if completion_mode == "evidence_backed" and evidence_count < 1:
        eligible = False
        reasons.append("No delivery evidence submitted")

    if completion_mode == "legacy":
        if task_status == "completed":
            eligible = True
            reasons = ["Legacy task — issuance permitted without evidence verification"]
        else:
            eligible = False
            reasons = [f"Legacy task but not completed (current: {task_status})"]

    return eligible, reasons
