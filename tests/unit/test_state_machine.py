"""Tests for app.domain.state_machine — transition validation."""

import pytest
from pydantic import ValidationError

from app.domain.state_machine import (
    APPLICATION_TRANSITIONS,
    PROJECT_TRANSITIONS,
    TASK_TRANSITIONS,
    validate_application_transition,
    validate_project_transition,
    validate_task_transition,
)
from app.exceptions import ConflictError
from app.schemas.task_card import UpdateTaskCardRequest

# ── Project transitions ───────────────────────────────────────────


class TestProjectTransitions:
    def test_valid_draft_to_open(self) -> None:
        validate_project_transition("draft", "open_for_collaboration")

    def test_valid_draft_to_closed(self) -> None:
        validate_project_transition("draft", "closed")

    def test_valid_open_to_team_forming(self) -> None:
        validate_project_transition("open_for_collaboration", "team_forming")

    def test_valid_in_progress_to_milestone_check(self) -> None:
        validate_project_transition("in_progress", "ready_for_milestone_check")

    def test_valid_delivered_to_closed(self) -> None:
        validate_project_transition("delivered", "closed")

    def test_valid_paused_to_in_progress(self) -> None:
        validate_project_transition("paused", "in_progress")

    def test_invalid_draft_to_in_progress(self) -> None:
        with pytest.raises(ConflictError, match="Cannot transition project"):
            validate_project_transition("draft", "in_progress")

    def test_invalid_closed_to_draft(self) -> None:
        with pytest.raises(ConflictError, match="Cannot transition project"):
            validate_project_transition("closed", "draft")

    def test_invalid_closed_has_no_transitions(self) -> None:
        # "closed" is a terminal state
        with pytest.raises(ConflictError):
            validate_project_transition("closed", "open_for_collaboration")

    def test_unknown_current_status(self) -> None:
        with pytest.raises(ConflictError, match="Unknown project status"):
            validate_project_transition("nonexistent", "draft")

    def test_all_project_states_have_entry(self) -> None:
        """Every state in the transitions dict should exist as a key."""
        all_states = set(PROJECT_TRANSITIONS.keys())
        # Every target state should also be a key (closed can be a target and has empty list)
        for targets in PROJECT_TRANSITIONS.values():
            for t in targets:
                assert t in all_states, f"Target state '{t}' not found as a key"

    def test_all_project_states_have_at_least_one_transition_except_archived(self) -> None:
        """Every non-terminal state should have at least one valid transition."""
        for state, targets in PROJECT_TRANSITIONS.items():
            if state == "archived":
                assert targets == []
            else:
                assert len(targets) >= 1, f"State '{state}' has no transitions"

    def test_valid_closed_to_archived(self) -> None:
        validate_project_transition("closed", "archived")

    def test_valid_delivered_to_archived(self) -> None:
        validate_project_transition("delivered", "archived")

    def test_invalid_archived_to_any(self) -> None:
        with pytest.raises(ConflictError):
            validate_project_transition("archived", "draft")


# ── Task transitions ──────────────────────────────────────────────


class TestTaskTransitions:
    def test_valid_draft_to_open(self) -> None:
        validate_task_transition("draft", "open")

    def test_valid_open_to_assigned(self) -> None:
        validate_task_transition("open", "assigned")

    def test_valid_assigned_to_in_progress(self) -> None:
        validate_task_transition("assigned", "in_progress")

    def test_valid_in_progress_to_submitted(self) -> None:
        validate_task_transition("in_progress", "submitted")

    def test_valid_submitted_to_under_review(self) -> None:
        validate_task_transition("submitted", "under_review")

    def test_valid_under_review_to_completed(self) -> None:
        validate_task_transition("under_review", "completed")

    def test_valid_rework_to_in_progress(self) -> None:
        validate_task_transition("rework_required", "in_progress")

    def test_valid_completed_to_closed(self) -> None:
        validate_task_transition("completed", "closed")

    def test_invalid_draft_to_completed(self) -> None:
        with pytest.raises(ConflictError, match="Cannot transition task"):
            validate_task_transition("draft", "completed")

    def test_invalid_closed_to_draft(self) -> None:
        with pytest.raises(ConflictError, match="Cannot transition task"):
            validate_task_transition("closed", "draft")

    def test_unknown_current_status(self) -> None:
        with pytest.raises(ConflictError, match="Unknown task status"):
            validate_task_transition("nonexistent", "open")

    def test_all_task_states_have_entry(self) -> None:
        """Every target state should also be a key in the dict."""
        all_states = set(TASK_TRANSITIONS.keys())
        for targets in TASK_TRANSITIONS.values():
            for t in targets:
                assert t in all_states, f"Target state '{t}' not found as a key"

    def test_all_task_states_have_at_least_one_transition_except_closed(self) -> None:
        """Every non-terminal state should have at least one valid transition."""
        for state, targets in TASK_TRANSITIONS.items():
            if state == "closed":
                assert targets == []
            else:
                assert len(targets) >= 1, f"State '{state}' has no transitions"


# ── Task update schema bypass prevention ─────────────────────────


class TestTaskUpdateSchemaBypassPrevention:
    """Verify that status cannot be set via the update schema."""

    def test_update_schema_rejects_status_field(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            UpdateTaskCardRequest(status="completed")

    def test_update_schema_rejects_unknown_fields(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            UpdateTaskCardRequest(arbitrary_field="value")

    def test_update_schema_allows_title(self) -> None:
        req = UpdateTaskCardRequest(title="New title")
        assert req.title == "New title"

    def test_update_schema_allows_goal(self) -> None:
        req = UpdateTaskCardRequest(goal="New goal")
        assert req.goal == "New goal"

    def test_update_schema_allows_ewu(self) -> None:
        from decimal import Decimal

        req = UpdateTaskCardRequest(ewu=Decimal("3.50"))
        assert req.ewu == Decimal("3.50")


# ── Application transitions ─────────────────────────────────────


class TestApplicationTransitions:
    def test_review_from_submitted_to_accepted(self) -> None:
        validate_application_transition("submitted", "accepted")

    def test_review_from_submitted_to_rejected(self) -> None:
        validate_application_transition("submitted", "rejected")

    def test_review_from_submitted_to_converted(self) -> None:
        validate_application_transition("submitted", "converted_to_growth_seat")

    def test_review_from_under_review_to_accepted(self) -> None:
        validate_application_transition("under_review", "accepted")

    def test_withdraw_from_submitted(self) -> None:
        validate_application_transition("submitted", "withdrawn")

    def test_withdraw_from_under_review(self) -> None:
        validate_application_transition("under_review", "withdrawn")

    def test_cannot_review_rejected_application(self) -> None:
        with pytest.raises(ConflictError, match="Cannot transition application"):
            validate_application_transition("rejected", "accepted")

    def test_cannot_review_withdrawn_application(self) -> None:
        with pytest.raises(ConflictError, match="Cannot transition application"):
            validate_application_transition("withdrawn", "accepted")

    def test_cannot_withdraw_accepted_application(self) -> None:
        with pytest.raises(ConflictError, match="Cannot transition application"):
            validate_application_transition("accepted", "withdrawn")

    def test_unknown_application_status(self) -> None:
        with pytest.raises(ConflictError, match="Unknown application status"):
            validate_application_transition("nonexistent", "accepted")

    def test_all_application_states_have_entry(self) -> None:
        all_states = set(APPLICATION_TRANSITIONS.keys())
        for targets in APPLICATION_TRANSITIONS.values():
            for t in targets:
                assert t in all_states, f"Target state '{t}' not found as a key"

    def test_terminal_states_have_no_transitions(self) -> None:
        terminal = ["accepted", "rejected", "converted_to_growth_seat", "withdrawn"]
        for state in terminal:
            assert APPLICATION_TRANSITIONS[state] == [], f"'{state}' should be terminal"
