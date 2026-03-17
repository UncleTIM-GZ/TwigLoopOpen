"""VC Agent — checks issuance eligibility and produces recommendation.

Phase 4.1: checks completion gate, verification status, evidence basis.
Does NOT issue VC directly — returns recommendation for platform to execute.
"""

from app.domain.a2a_protocol import AgentResult, DelegationContract, TaskEnvelope


async def run_vc_agent(envelope: TaskEnvelope, contract: DelegationContract) -> AgentResult:
    """Check VC issuance eligibility and produce recommendation."""
    task_status = envelope.current_status
    verification_status = envelope.signal_context.get("verification_status", "unverified")
    completion_mode = envelope.signal_context.get("completion_mode", "evidence_backed")
    evidence_count = envelope.signal_context.get("evidence_count", 0)
    ewu = envelope.constraints.get("ewu", "0")
    actor_id = envelope.signal_context.get("target_actor_id", "")

    reasons: list[str] = []
    eligible = True

    # Check completion
    if task_status != "completed":
        eligible = False
        reasons.append(f"Task not completed (current: {task_status})")

    # Check verification
    if completion_mode == "evidence_backed" and verification_status != "verified":
        eligible = False
        reasons.append(f"Verification required but status is: {verification_status}")

    # Check evidence
    if completion_mode == "evidence_backed" and evidence_count < 1:
        eligible = False
        reasons.append("No delivery evidence submitted")

    # Legacy tasks get a pass
    if completion_mode == "legacy":
        eligible = True
        reasons = ["Legacy task — issuance permitted without evidence verification"]

    if eligible:
        decision = "recommend_issue"
        summary = f"VC issuance recommended for task (EWU: {ewu}). All gates passed."
        basis = "verified" if completion_mode == "evidence_backed" else "legacy"
    else:
        decision = "deny"
        summary = f"VC issuance denied: {'; '.join(reasons)}"
        basis = "none"

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
        },
        confidence=0.95 if eligible else 0.9,
        requires_human_review=not eligible,
    )
