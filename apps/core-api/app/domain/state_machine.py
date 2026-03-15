"""State machine definitions from .docs/ Schema 草案 Section 7."""

from app.exceptions import ConflictError

# Project status transitions (Section 7.1)
PROJECT_TRANSITIONS: dict[str, list[str]] = {
    "draft": ["open_for_collaboration", "closed"],
    "open_for_collaboration": ["team_forming", "closed"],
    "team_forming": ["reviewer_required", "in_progress", "paused"],
    "reviewer_required": ["in_progress", "paused"],
    "in_progress": ["ready_for_milestone_check", "paused"],
    "ready_for_milestone_check": ["human_review_passed", "in_progress"],
    "human_review_passed": ["delivered", "in_progress"],
    "delivered": ["closed", "archived"],
    "paused": ["in_progress", "closed"],
    "closed": ["archived"],
    "archived": [],
}

# Task status transitions (Section 7.2)
TASK_TRANSITIONS: dict[str, list[str]] = {
    "draft": ["open"],
    "open": ["assigned", "closed"],
    "assigned": ["in_progress", "closed"],
    "in_progress": ["submitted", "rework_required"],
    "submitted": ["under_review", "completed"],
    "under_review": ["completed", "rework_required"],
    "rework_required": ["in_progress", "closed"],
    "completed": ["closed"],
    "closed": [],
}


def validate_project_transition(current: str, target: str) -> None:
    """Raise ConflictError if the transition is not allowed."""
    if current not in PROJECT_TRANSITIONS:
        raise ConflictError(f"Unknown project status: '{current}'")
    allowed = PROJECT_TRANSITIONS[current]
    if target not in allowed:
        raise ConflictError(
            f"Cannot transition project from '{current}' to '{target}'. Allowed: {allowed}"
        )


# Application status transitions (Section 7.3)
# NOTE: "under_review" is a reserved future state. No API endpoint currently
# triggers the submitted -> under_review transition. The ReviewApplicationRequest
# Literal only allows accepted/rejected/converted_to_growth_seat as decisions.
# When a separate "start review" step is needed, add an API endpoint for it.
APPLICATION_TRANSITIONS: dict[str, list[str]] = {
    "submitted": ["under_review", "accepted", "rejected", "converted_to_growth_seat", "withdrawn"],
    "under_review": ["accepted", "rejected", "converted_to_growth_seat", "withdrawn"],
    "accepted": [],
    "rejected": [],
    "converted_to_growth_seat": [],
    "withdrawn": [],
}


def validate_application_transition(current: str, target: str) -> None:
    """Raise ConflictError if the application transition is not allowed."""
    if current not in APPLICATION_TRANSITIONS:
        raise ConflictError(f"Unknown application status: '{current}'")
    allowed = APPLICATION_TRANSITIONS[current]
    if target not in allowed:
        raise ConflictError(
            f"Cannot transition application from '{current}' to '{target}'. Allowed: {allowed}"
        )


def validate_task_transition(current: str, target: str) -> None:
    """Raise ConflictError if the transition is not allowed."""
    if current not in TASK_TRANSITIONS:
        raise ConflictError(f"Unknown task status: '{current}'")
    allowed = TASK_TRANSITIONS[current]
    if target not in allowed:
        raise ConflictError(
            f"Cannot transition task from '{current}' to '{target}'. Allowed: {allowed}"
        )
