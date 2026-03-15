"""Golden path: A publishes project -> B applies -> A accepts -> B completes task.

This is Chain 1 from the test plan (GP-001 ~ GP-004).
Tests the most common collaboration flow for a general project.

These are integration-level tests that describe the EXPECTED flow.
They use mock session/data since we don't have a real DB in CI yet.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Lightweight in-memory stubs for scenario testing without a live database.
# These mirror the real domain objects just enough to validate business logic.
# ---------------------------------------------------------------------------

PROJECT_TRANSITIONS: dict[str, list[str]] = {
    "draft": ["open_for_collaboration", "closed"],
    "open_for_collaboration": ["team_forming", "closed"],
    "team_forming": ["reviewer_required", "in_progress", "paused"],
    "reviewer_required": ["in_progress", "paused"],
    "in_progress": ["ready_for_milestone_check", "paused"],
    "ready_for_milestone_check": ["human_review_passed", "in_progress"],
    "human_review_passed": ["delivered", "in_progress"],
    "delivered": ["closed"],
    "paused": ["in_progress", "closed"],
    "closed": [],
}

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


class TransitionError(Exception):
    """Raised when a state transition is not allowed."""


def validate_project_transition(current: str, target: str) -> None:
    allowed = PROJECT_TRANSITIONS.get(current, [])
    if target not in allowed:
        raise TransitionError(
            f"Cannot transition project from '{current}' to '{target}'. Allowed: {allowed}"
        )


def validate_task_transition(current: str, target: str) -> None:
    allowed = TASK_TRANSITIONS.get(current, [])
    if target not in allowed:
        raise TransitionError(
            f"Cannot transition task from '{current}' to '{target}'. Allowed: {allowed}"
        )


@dataclass
class ScenarioProject:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    founder_actor_id: str = ""
    project_type: str = "general"
    title: str = "Test Project"
    status: str = "draft"
    needs_human_reviewer: bool = False

    def transition_to(self, target: str) -> None:
        validate_project_transition(self.status, target)
        self.status = target


@dataclass
class ScenarioWorkPackage:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    title: str = "Test WP"
    status: str = "draft"


@dataclass
class ScenarioTask:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    work_package_id: str = ""
    title: str = "Test Task"
    status: str = "draft"
    ewu: Decimal = field(default_factory=lambda: Decimal("4.0"))
    assignee_id: str | None = None

    def transition_to(self, target: str) -> None:
        validate_task_transition(self.status, target)
        self.status = target


@dataclass
class ScenarioApplication:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    actor_id: str = ""
    status: str = "submitted"


@dataclass
class ScenarioSeat:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    actor_id: str = ""
    seat_type: str = "growth"
    status: str = "on_trial"


# ---------------------------------------------------------------------------
# In-memory store for the scenario
# ---------------------------------------------------------------------------


class ScenarioStore:
    """Simple in-memory store to track objects through the golden path."""

    def __init__(self) -> None:
        self.projects: dict[str, ScenarioProject] = {}
        self.work_packages: dict[str, ScenarioWorkPackage] = {}
        self.tasks: dict[str, ScenarioTask] = {}
        self.applications: dict[str, ScenarioApplication] = {}
        self.seats: dict[str, ScenarioSeat] = {}
        self.signals: list[dict[str, Any]] = []

    def create_project(self, founder_id: str, **kwargs: Any) -> ScenarioProject:
        project = ScenarioProject(founder_actor_id=founder_id, **kwargs)
        self.projects[project.id] = project
        return project

    def create_work_package(self, project_id: str, **kwargs: Any) -> ScenarioWorkPackage:
        wp = ScenarioWorkPackage(project_id=project_id, **kwargs)
        self.work_packages[wp.id] = wp
        return wp

    def create_task(self, wp_id: str, **kwargs: Any) -> ScenarioTask:
        task = ScenarioTask(work_package_id=wp_id, **kwargs)
        self.tasks[task.id] = task
        return task

    def create_application(self, project_id: str, actor_id: str) -> ScenarioApplication:
        app = ScenarioApplication(project_id=project_id, actor_id=actor_id)
        self.applications[app.id] = app
        return app

    def accept_application(self, app_id: str) -> ScenarioSeat:
        app = self.applications[app_id]
        app.status = "accepted"
        seat = ScenarioSeat(
            project_id=app.project_id,
            actor_id=app.actor_id,
        )
        self.seats[seat.id] = seat
        return seat

    def reject_application(self, app_id: str) -> None:
        self.applications[app_id].status = "rejected"

    def add_signal(self, project_id: str, signal_type: str) -> dict[str, str]:
        signal = {"project_id": project_id, "signal_type": signal_type}
        self.signals.append(signal)
        return signal


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestGoldenPathGeneral:
    """Chain 1: General project normal startup.

    A publishes project -> B applies -> A accepts -> B completes task.
    """

    @pytest.fixture(autouse=True)
    def setup_store(self) -> None:
        self.store = ScenarioStore()
        self.founder_id = str(uuid.uuid4())
        self.collaborator_id = str(uuid.uuid4())

    def test_a_creates_project(self) -> None:
        """GP-001: A can create a draft and commit a general project."""
        project = self.store.create_project(
            self.founder_id,
            title="AI Research Assistant MVP",
            project_type="general",
        )

        assert project.status == "draft"
        assert project.project_type == "general"
        assert project.founder_actor_id == self.founder_id
        assert project.id in self.store.projects

    def test_a_adds_work_package_and_tasks(self) -> None:
        """GP-001 continued: A structures the project with WP and tasks."""
        project = self.store.create_project(self.founder_id)
        wp = self.store.create_work_package(project.id, title="Landing Page MVP")
        task = self.store.create_task(
            wp.id,
            title="Create landing page layout",
            ewu=Decimal("3.0"),
        )

        assert wp.project_id == project.id
        assert task.work_package_id == wp.id
        assert task.ewu == Decimal("3.0")

    def test_a_publishes_project(self) -> None:
        """GP-001: A publishes the project (draft -> open_for_collaboration)."""
        project = self.store.create_project(self.founder_id)
        self.store.create_work_package(project.id)

        project.transition_to("open_for_collaboration")

        assert project.status == "open_for_collaboration"

    def test_b_applies_to_project(self) -> None:
        """GP-002: B can apply to an open project."""
        project = self.store.create_project(self.founder_id, status="open_for_collaboration")
        app = self.store.create_application(project.id, self.collaborator_id)

        assert app.status == "submitted"
        assert app.project_id == project.id
        assert app.actor_id == self.collaborator_id

    def test_a_accepts_application(self) -> None:
        """GP-003: A can accept B's application and create a seat."""
        project = self.store.create_project(self.founder_id, status="open_for_collaboration")
        app = self.store.create_application(project.id, self.collaborator_id)

        seat = self.store.accept_application(app.id)

        assert app.status == "accepted"
        assert seat.actor_id == self.collaborator_id
        assert seat.project_id == project.id
        assert seat.seat_type == "growth"
        assert seat.status == "on_trial"

    def test_b_completes_task(self) -> None:
        """GP-004: B can transition task through the full lifecycle to completed."""
        project = self.store.create_project(self.founder_id, status="open_for_collaboration")
        wp = self.store.create_work_package(project.id)
        task = self.store.create_task(wp.id, title="Build the landing page")

        # Task lifecycle: draft -> open -> assigned -> in_progress -> submitted -> completed
        task.transition_to("open")
        assert task.status == "open"

        task.transition_to("assigned")
        task.assignee_id = self.collaborator_id
        assert task.status == "assigned"

        task.transition_to("in_progress")
        assert task.status == "in_progress"

        task.transition_to("submitted")
        assert task.status == "submitted"

        task.transition_to("completed")
        assert task.status == "completed"

    def test_task_completion_generates_signal(self) -> None:
        """GP-004: Completing a task produces a progress signal."""
        project = self.store.create_project(self.founder_id)
        signal = self.store.add_signal(project.id, "task_completed")

        assert signal["signal_type"] == "task_completed"
        assert signal["project_id"] == project.id
        assert len(self.store.signals) == 1

    def test_full_golden_path_end_to_end(self) -> None:
        """GP-001~004 combined: Full chain from creation to task completion."""
        # A creates and publishes
        project = self.store.create_project(
            self.founder_id,
            title="Full Golden Path Project",
        )
        wp = self.store.create_work_package(project.id, title="Core Feature")
        task = self.store.create_task(wp.id, title="Implement core logic", ewu=Decimal("4.0"))

        project.transition_to("open_for_collaboration")
        assert project.status == "open_for_collaboration"

        # B discovers and applies
        app = self.store.create_application(project.id, self.collaborator_id)
        assert app.status == "submitted"

        # A accepts
        seat = self.store.accept_application(app.id)
        assert seat.status == "on_trial"

        # B completes the task
        task.transition_to("open")
        task.transition_to("assigned")
        task.assignee_id = self.collaborator_id
        task.transition_to("in_progress")
        task.transition_to("submitted")
        task.transition_to("completed")

        # Signal recorded
        self.store.add_signal(project.id, "task_completed")

        # Final assertions
        assert project.status == "open_for_collaboration"
        assert app.status == "accepted"
        assert task.status == "completed"
        assert len(self.store.signals) == 1
        assert self.store.signals[0]["signal_type"] == "task_completed"
