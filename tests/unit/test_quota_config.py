"""Tests for app.domain.quota_config constants."""

from app.domain.quota_config import (
    ACTIVE_PROJECT_STATUSES,
    ACTIVE_TASK_STATUSES,
    MAX_ACTIVE_PROJECTS_NEW_FOUNDER,
    MAX_ACTIVE_TASKS_DEFAULT,
    MAX_EWU_PER_TASK,
    MAX_OPEN_SEATS_DEFAULT,
    MAX_PENDING_APPLICATIONS_PER_PROJECT,
    MAX_PENDING_APPLICATIONS_PER_TASK,
    MAX_TASKS_PER_PROJECT,
    MAX_TASKS_PER_WORK_PACKAGE,
    MAX_WORK_PACKAGES_PER_PROJECT,
    OPEN_SEAT_STATUSES,
    PENDING_APPLICATION_STATUSES,
)

# ── Object volume limits ─────────────────────────────────────────


class TestObjectLimits:
    def test_max_work_packages_per_project(self) -> None:
        assert MAX_WORK_PACKAGES_PER_PROJECT == 5

    def test_max_tasks_per_work_package(self) -> None:
        assert MAX_TASKS_PER_WORK_PACKAGE == 6

    def test_max_tasks_per_project(self) -> None:
        assert MAX_TASKS_PER_PROJECT == 20

    def test_max_ewu_per_task(self) -> None:
        assert MAX_EWU_PER_TASK == 8


# ── Founder concurrency limits ───────────────────────────────────


class TestFounderLimits:
    def test_max_active_projects_new_founder(self) -> None:
        assert MAX_ACTIVE_PROJECTS_NEW_FOUNDER == 2

    def test_max_open_seats_default(self) -> None:
        assert MAX_OPEN_SEATS_DEFAULT == 12

    def test_max_active_tasks_default(self) -> None:
        assert MAX_ACTIVE_TASKS_DEFAULT == 30


# ── Relationship limits ──────────────────────────────────────────


class TestRelationshipLimits:
    def test_max_pending_applications_per_project(self) -> None:
        assert MAX_PENDING_APPLICATIONS_PER_PROJECT == 30

    def test_max_pending_applications_per_task(self) -> None:
        assert MAX_PENDING_APPLICATIONS_PER_TASK == 10


# ── Status tuples ────────────────────────────────────────────────


class TestStatusTuples:
    def test_active_project_statuses(self) -> None:
        assert ACTIVE_PROJECT_STATUSES == ("draft", "published", "open", "in_progress")

    def test_open_seat_statuses(self) -> None:
        assert OPEN_SEAT_STATUSES == ("proposed", "on_trial")

    def test_active_task_statuses(self) -> None:
        assert ACTIVE_TASK_STATUSES == ("draft", "assigned", "in_progress", "submitted")

    def test_pending_application_statuses(self) -> None:
        assert PENDING_APPLICATION_STATUSES == ("submitted", "under_review")

    def test_all_status_tuples_are_tuples_of_strings(self) -> None:
        for statuses in (
            ACTIVE_PROJECT_STATUSES,
            OPEN_SEAT_STATUSES,
            ACTIVE_TASK_STATUSES,
            PENDING_APPLICATION_STATUSES,
        ):
            assert isinstance(statuses, tuple)
            for s in statuses:
                assert isinstance(s, str)

    def test_no_duplicate_statuses(self) -> None:
        for statuses in (
            ACTIVE_PROJECT_STATUSES,
            OPEN_SEAT_STATUSES,
            ACTIVE_TASK_STATUSES,
            PENDING_APPLICATION_STATUSES,
        ):
            assert len(statuses) == len(set(statuses)), f"Duplicate found in {statuses}"
