"""Review Prep Agent — prepares evidence review brief for reviewers.

Phase 4 minimum: structured summary of evidence, no quality judgment.
Future: LLM-powered review assistance.
"""

from app.domain.a2a_protocol import AgentResult, DelegationContract, TaskEnvelope


async def run_review_prep_agent(
    envelope: TaskEnvelope, contract: DelegationContract
) -> AgentResult:
    """Prepare a review brief from task evidence context."""
    evidence_reqs = envelope.evidence_requirements
    criteria = envelope.completion_criteria
    signals = envelope.signal_context

    brief_items: list[str] = []
    brief_items.append(f"Task objective: {envelope.objective}")

    if criteria:
        brief_items.append(f"Completion criteria: {criteria}")

    if evidence_reqs:
        brief_items.append(f"Required evidence types: {', '.join(evidence_reqs)}")
    else:
        brief_items.append("No specific evidence type requirements defined.")

    if signals.get("evidence_count", 0) > 0:
        brief_items.append(f"Evidence submitted: {signals['evidence_count']} items")
    else:
        brief_items.append("No evidence submitted yet.")

    if signals.get("repo_url"):
        brief_items.append(f"Repository: {signals['repo_url']}")

    checklist = [
        "Verify evidence URLs are accessible",
        "Check if deliverables match output_spec",
        "Confirm completion_criteria are met",
        "Assess if evidence is sufficient for EWU claim",
    ]

    return AgentResult(
        delegation_id=contract.delegation_id,
        result_type="review_brief",
        summary="\n".join(brief_items),
        structured_payload={
            "review_brief": brief_items,
            "review_checklist": checklist,
            "evidence_count": signals.get("evidence_count", 0),
            "has_repo": bool(signals.get("repo_url")),
            "recommendation": (
                "Review evidence before approving"
                if signals.get("evidence_count", 0) > 0
                else "Wait for evidence submission"
            ),
        },
        confidence=0.6,
        requires_human_review=True,
    )
