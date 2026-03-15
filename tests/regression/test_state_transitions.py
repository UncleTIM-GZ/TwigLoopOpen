"""Regression tests for state transition edge cases.

These tests capture past bugs and edge cases to prevent regressions
in the state machine logic.
"""

import pytest
from app.domain.state_machine import (
    PROJECT_TRANSITIONS,
    TASK_TRANSITIONS,
    validate_project_transition,
    validate_task_transition,
)
from app.exceptions import ConflictError


class TestProjectTransitionRegression:
    """Regression tests for project state machine edge cases."""

    def test_paused_cannot_go_back_to_draft(self):
        """Bug: paused projects could be reverted to draft."""
        with pytest.raises(ConflictError):
            validate_project_transition("paused", "draft")

    def test_paused_cannot_go_to_open(self):
        """Bug: paused projects could go directly to open_for_collaboration."""
        with pytest.raises(ConflictError):
            validate_project_transition("paused", "open_for_collaboration")

    def test_delivered_can_close_or_archive(self):
        """Delivered projects can transition to closed or archived."""
        validate_project_transition("delivered", "closed")
        validate_project_transition("delivered", "archived")
        for status in PROJECT_TRANSITIONS:
            if status not in ("closed", "archived"):
                with pytest.raises(ConflictError):
                    validate_project_transition("delivered", status)

    def test_milestone_check_revert_to_in_progress(self):
        """Ready_for_milestone_check can revert to in_progress (rework)."""
        validate_project_transition("ready_for_milestone_check", "in_progress")

    def test_reviewer_required_cannot_skip_to_delivered(self):
        """Reviewer_required cannot skip directly to delivered."""
        with pytest.raises(ConflictError):
            validate_project_transition("reviewer_required", "delivered")

    def test_all_reachable_states_are_valid(self):
        """Every target state should be a key in the transition map."""
        for source, targets in PROJECT_TRANSITIONS.items():
            for target in targets:
                assert target in PROJECT_TRANSITIONS, (
                    f"Target '{target}' from '{source}' is not a valid state"
                )

    def test_no_self_transitions(self):
        """No state should transition to itself."""
        for status, targets in PROJECT_TRANSITIONS.items():
            assert status not in targets, (
                f"State '{status}' has self-transition which is not allowed"
            )


class TestTaskTransitionRegression:
    """Regression tests for task state machine edge cases."""

    def test_closed_is_terminal(self):
        """Closed tasks cannot transition to any other state."""
        for target in TASK_TRANSITIONS:
            if target == "closed":
                continue
            with pytest.raises(ConflictError):
                validate_task_transition("closed", target)

    def test_completed_can_only_close(self):
        """Completed tasks can only be closed."""
        validate_task_transition("completed", "closed")
        for target in TASK_TRANSITIONS:
            if target not in ("closed", "completed"):
                with pytest.raises(ConflictError):
                    validate_task_transition("completed", target)

    def test_rework_required_to_in_progress(self):
        """Rework can loop back to in_progress."""
        validate_task_transition("rework_required", "in_progress")

    def test_rework_required_to_closed(self):
        """Rework can be abandoned (closed)."""
        validate_task_transition("rework_required", "closed")

    def test_rework_required_cannot_go_to_submitted(self):
        """Rework must go through in_progress before resubmitting."""
        with pytest.raises(ConflictError):
            validate_task_transition("rework_required", "submitted")

    def test_submitted_cannot_go_back_to_in_progress(self):
        """Once submitted, a task cannot revert to in_progress directly."""
        with pytest.raises(ConflictError):
            validate_task_transition("submitted", "in_progress")

    def test_assigned_cannot_skip_to_submitted(self):
        """Assigned tasks must go through in_progress first."""
        with pytest.raises(ConflictError):
            validate_task_transition("assigned", "submitted")

    def test_full_happy_path_chain(self):
        """Verify the complete happy path chain succeeds."""
        chain = [
            ("draft", "open"),
            ("open", "assigned"),
            ("assigned", "in_progress"),
            ("in_progress", "submitted"),
            ("submitted", "under_review"),
            ("under_review", "completed"),
            ("completed", "closed"),
        ]
        for current, target in chain:
            validate_task_transition(current, target)

    def test_rework_loop(self):
        """Verify the rework loop: in_progress -> rework_required -> in_progress."""
        validate_task_transition("in_progress", "rework_required")
        validate_task_transition("rework_required", "in_progress")
        validate_task_transition("in_progress", "submitted")

    def test_no_self_transitions(self):
        """No task state should transition to itself."""
        for status, targets in TASK_TRANSITIONS.items():
            assert status not in targets, (
                f"Task state '{status}' has self-transition which is not allowed"
            )

    def test_all_reachable_states_are_valid(self):
        """Every target state should be a key in the transition map."""
        for source, targets in TASK_TRANSITIONS.items():
            for target in targets:
                assert target in TASK_TRANSITIONS, (
                    f"Target '{target}' from '{source}' is not a valid state"
                )


# ---------------------------------------------------------------------------
# Exhaustive valid transition coverage
# ---------------------------------------------------------------------------


class TestProjectAllValidTransitions:
    """Verify every valid transition in PROJECT_TRANSITIONS succeeds."""

    def test_draft_to_open_for_collaboration(self):
        validate_project_transition("draft", "open_for_collaboration")

    def test_draft_to_closed(self):
        validate_project_transition("draft", "closed")

    def test_open_to_team_forming(self):
        validate_project_transition("open_for_collaboration", "team_forming")

    def test_open_to_closed(self):
        validate_project_transition("open_for_collaboration", "closed")

    def test_team_forming_to_reviewer_required(self):
        validate_project_transition("team_forming", "reviewer_required")

    def test_team_forming_to_in_progress(self):
        validate_project_transition("team_forming", "in_progress")

    def test_team_forming_to_paused(self):
        validate_project_transition("team_forming", "paused")

    def test_reviewer_required_to_in_progress(self):
        validate_project_transition("reviewer_required", "in_progress")

    def test_reviewer_required_to_paused(self):
        validate_project_transition("reviewer_required", "paused")

    def test_in_progress_to_milestone_check(self):
        validate_project_transition("in_progress", "ready_for_milestone_check")

    def test_in_progress_to_paused(self):
        validate_project_transition("in_progress", "paused")

    def test_milestone_check_to_review_passed(self):
        validate_project_transition("ready_for_milestone_check", "human_review_passed")

    def test_milestone_check_to_in_progress(self):
        validate_project_transition("ready_for_milestone_check", "in_progress")

    def test_review_passed_to_delivered(self):
        validate_project_transition("human_review_passed", "delivered")

    def test_review_passed_to_in_progress(self):
        validate_project_transition("human_review_passed", "in_progress")

    def test_delivered_to_closed(self):
        validate_project_transition("delivered", "closed")

    def test_paused_to_in_progress(self):
        validate_project_transition("paused", "in_progress")

    def test_paused_to_closed(self):
        validate_project_transition("paused", "closed")


class TestProjectAllInvalidTransitions:
    """Verify every invalid (current, target) pair is rejected."""

    def test_exhaustive_invalid_project_transitions(self):
        """Every pair NOT in the allowed list raises ConflictError."""
        all_statuses = list(PROJECT_TRANSITIONS.keys())
        for current, allowed_targets in PROJECT_TRANSITIONS.items():
            for target in all_statuses:
                if target in allowed_targets:
                    validate_project_transition(current, target)
                else:
                    with pytest.raises(ConflictError):
                        validate_project_transition(current, target)

    def test_invalid_draft_to_in_progress(self):
        with pytest.raises(ConflictError):
            validate_project_transition("draft", "in_progress")

    def test_invalid_draft_to_delivered(self):
        with pytest.raises(ConflictError):
            validate_project_transition("draft", "delivered")

    def test_invalid_closed_to_draft(self):
        with pytest.raises(ConflictError):
            validate_project_transition("closed", "draft")

    def test_invalid_open_to_in_progress(self):
        with pytest.raises(ConflictError):
            validate_project_transition("open_for_collaboration", "in_progress")


class TestTaskAllValidTransitions:
    """Verify every valid transition in TASK_TRANSITIONS succeeds."""

    def test_draft_to_open(self):
        validate_task_transition("draft", "open")

    def test_open_to_assigned(self):
        validate_task_transition("open", "assigned")

    def test_open_to_closed(self):
        validate_task_transition("open", "closed")

    def test_assigned_to_in_progress(self):
        validate_task_transition("assigned", "in_progress")

    def test_assigned_to_closed(self):
        validate_task_transition("assigned", "closed")

    def test_in_progress_to_submitted(self):
        validate_task_transition("in_progress", "submitted")

    def test_in_progress_to_rework_required(self):
        validate_task_transition("in_progress", "rework_required")

    def test_submitted_to_under_review(self):
        validate_task_transition("submitted", "under_review")

    def test_submitted_to_completed(self):
        validate_task_transition("submitted", "completed")

    def test_under_review_to_completed(self):
        validate_task_transition("under_review", "completed")

    def test_under_review_to_rework_required(self):
        validate_task_transition("under_review", "rework_required")

    def test_rework_to_in_progress(self):
        validate_task_transition("rework_required", "in_progress")

    def test_rework_to_closed(self):
        validate_task_transition("rework_required", "closed")

    def test_completed_to_closed(self):
        validate_task_transition("completed", "closed")


class TestTaskAllInvalidTransitions:
    """Verify every invalid (current, target) pair is rejected."""

    def test_exhaustive_invalid_task_transitions(self):
        all_statuses = list(TASK_TRANSITIONS.keys())
        for current, allowed_targets in TASK_TRANSITIONS.items():
            for target in all_statuses:
                if target in allowed_targets:
                    validate_task_transition(current, target)
                else:
                    with pytest.raises(ConflictError):
                        validate_task_transition(current, target)

    def test_invalid_draft_to_completed(self):
        with pytest.raises(ConflictError):
            validate_task_transition("draft", "completed")

    def test_invalid_draft_to_assigned(self):
        with pytest.raises(ConflictError):
            validate_task_transition("draft", "assigned")

    def test_invalid_completed_to_draft(self):
        with pytest.raises(ConflictError):
            validate_task_transition("completed", "draft")

    def test_invalid_closed_to_open(self):
        with pytest.raises(ConflictError):
            validate_task_transition("closed", "open")
