"""Matching Agent — analyzes projects and applications to suggest matches.

Phase 4 minimum: rule-based matching, no LLM.
Future: LLM-powered analysis via A2A external endpoint.
"""

from app.domain.a2a_protocol import AgentResult, DelegationContract, TaskEnvelope


async def run_matching_agent(envelope: TaskEnvelope, contract: DelegationContract) -> AgentResult:
    """Analyze task context and produce matching suggestions."""
    suggestions: list[str] = []

    # Rule-based matching logic
    task_type = envelope.constraints.get("task_type", "")
    main_role = envelope.constraints.get("main_role", "")
    ewu = float(envelope.constraints.get("ewu", 0))

    if task_type == "development":
        suggestions.append(f"This is a development task requiring a {main_role}.")
        if ewu >= 6:
            suggestions.append("High complexity (EWU >= 6) — recommend experienced developers.")
        else:
            suggestions.append("Moderate complexity — suitable for growth seat candidates.")
    elif task_type == "product_design":
        suggestions.append("Design task — look for candidates with design portfolio.")
    else:
        suggestions.append(f"Task type: {task_type} — match based on {main_role} skills.")

    # Seat recommendation
    if ewu >= 5:
        seat_suggestion = "formal"
        suggestions.append("Recommend formal seat for high-EWU task.")
    else:
        seat_suggestion = "growth"
        suggestions.append("Growth seat appropriate for this complexity level.")

    return AgentResult(
        delegation_id=contract.delegation_id,
        result_type="matching_suggestion",
        summary=" ".join(suggestions),
        structured_payload={
            "recommended_seat_type": seat_suggestion,
            "skill_requirements": [main_role, task_type],
            "complexity_level": "high" if ewu >= 6 else "moderate" if ewu >= 3 else "low",
            "matching_notes": suggestions,
        },
        confidence=0.7,
        requires_human_review=True,
    )
