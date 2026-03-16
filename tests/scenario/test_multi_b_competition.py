"""Multi-B competition: Multiple collaborators competing for the same project.

This is Chain 5 from the test plan (GP-016 ~ GP-019).
Tests application limits, concurrent applications, accept/reject flows.

These are integration-level tests that describe the EXPECTED flow.
They use mock session/data since we don't have a real DB in CI yet.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_APPLICATIONS_PER_PROJECT = 30

# ---------------------------------------------------------------------------
# In-memory domain objects
# ---------------------------------------------------------------------------


@dataclass
class CompetitionProject:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    founder_actor_id: str = ""
    title: str = "Competition Project"
    status: str = "open_for_collaboration"


@dataclass
class CompetitionApplication:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    actor_id: str = ""
    status: str = "submitted"
    seat_preference: str = "growth"
    intended_role: str = "developer"


@dataclass
class CompetitionSeat:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    actor_id: str = ""
    seat_type: str = "growth"
    status: str = "on_trial"


class ApplicationLimitExceeded(Exception):
    """Raised when the application limit per project is exceeded."""


class DuplicateApplicationError(Exception):
    """Raised when the same actor applies twice to the same project."""


class CompetitionStore:
    """In-memory store for multi-B competition scenario."""

    def __init__(self) -> None:
        self.projects: dict[str, CompetitionProject] = {}
        self.applications: dict[str, CompetitionApplication] = {}
        self.seats: dict[str, CompetitionSeat] = {}

    def create_project(self, founder_id: str, **kwargs: Any) -> CompetitionProject:
        project = CompetitionProject(founder_actor_id=founder_id, **kwargs)
        self.projects[project.id] = project
        return project

    def get_application_count(self, project_id: str) -> int:
        return sum(
            1 for app in self.applications.values() if app.project_id == project_id
        )

    def has_existing_application(self, project_id: str, actor_id: str) -> bool:
        return any(
            app.project_id == project_id and app.actor_id == actor_id
            for app in self.applications.values()
        )

    def apply(self, project_id: str, actor_id: str, **kwargs: Any) -> CompetitionApplication:
        # Check duplicate
        if self.has_existing_application(project_id, actor_id):
            raise DuplicateApplicationError(
                f"Actor {actor_id} already applied to project {project_id}"
            )

        # Check limit
        count = self.get_application_count(project_id)
        if count >= MAX_APPLICATIONS_PER_PROJECT:
            raise ApplicationLimitExceeded(
                f"Project {project_id} has reached the maximum of "
                f"{MAX_APPLICATIONS_PER_PROJECT} applications"
            )

        app = CompetitionApplication(
            project_id=project_id,
            actor_id=actor_id,
            **kwargs,
        )
        self.applications[app.id] = app
        return app

    def accept_application(self, app_id: str) -> CompetitionSeat:
        app = self.applications[app_id]
        app.status = "accepted"
        seat = CompetitionSeat(
            project_id=app.project_id,
            actor_id=app.actor_id,
        )
        self.seats[seat.id] = seat
        return seat

    def reject_application(self, app_id: str) -> None:
        self.applications[app_id].status = "rejected"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMultiBCompetition:
    """Chain 5: Multiple B actors competing for the same project.

    A publishes project -> B1, B2, B3... apply -> A selects -> others rejected.
    """

    @pytest.fixture(autouse=True)
    def setup_store(self) -> None:
        self.store = CompetitionStore()
        self.founder_id = str(uuid.uuid4())
        self.project = self.store.create_project(
            self.founder_id, title="Hot AI Project"
        )

    def _make_actor_id(self) -> str:
        return str(uuid.uuid4())

    def test_multiple_applications_allowed(self) -> None:
        """GP-016: Multiple Bs can apply to the same project independently."""
        b1 = self._make_actor_id()
        b2 = self._make_actor_id()
        b3 = self._make_actor_id()

        app1 = self.store.apply(self.project.id, b1)
        app2 = self.store.apply(self.project.id, b2)
        app3 = self.store.apply(self.project.id, b3)

        assert app1.status == "submitted"
        assert app2.status == "submitted"
        assert app3.status == "submitted"
        assert self.store.get_application_count(self.project.id) == 3

    def test_duplicate_application_blocked(self) -> None:
        """Same actor cannot apply twice to the same project."""
        b1 = self._make_actor_id()
        self.store.apply(self.project.id, b1)

        with pytest.raises(DuplicateApplicationError):
            self.store.apply(self.project.id, b1)

    def test_application_limit_30_allowed(self) -> None:
        """QT-023: Up to 30 applications per project are allowed."""
        for i in range(30):
            actor_id = self._make_actor_id()
            app = self.store.apply(self.project.id, actor_id)
            assert app.status == "submitted"

        assert self.store.get_application_count(self.project.id) == 30

    def test_application_limit_enforced(self) -> None:
        """QT-024: 31st application is blocked."""
        for _ in range(MAX_APPLICATIONS_PER_PROJECT):
            self.store.apply(self.project.id, self._make_actor_id())

        with pytest.raises(ApplicationLimitExceeded):
            self.store.apply(self.project.id, self._make_actor_id())

    def test_accepted_b_gets_seat(self) -> None:
        """GP-017: Accepted B gets a project seat."""
        b1 = self._make_actor_id()
        app = self.store.apply(self.project.id, b1)

        seat = self.store.accept_application(app.id)

        assert app.status == "accepted"
        assert seat.actor_id == b1
        assert seat.project_id == self.project.id
        assert seat.seat_type == "growth"
        assert seat.status == "on_trial"

    def test_rejected_b_status_correct(self) -> None:
        """GP-018: Rejected B's application status is 'rejected'."""
        b1 = self._make_actor_id()
        app = self.store.apply(self.project.id, b1)

        self.store.reject_application(app.id)

        assert app.status == "rejected"

    def test_selective_accept_and_reject(self) -> None:
        """GP-017/018: A accepts B1, rejects B2 and B3."""
        b1 = self._make_actor_id()
        b2 = self._make_actor_id()
        b3 = self._make_actor_id()

        app1 = self.store.apply(self.project.id, b1)
        app2 = self.store.apply(self.project.id, b2)
        app3 = self.store.apply(self.project.id, b3)

        # A accepts B1
        seat = self.store.accept_application(app1.id)
        assert seat.actor_id == b1

        # A rejects B2 and B3
        self.store.reject_application(app2.id)
        self.store.reject_application(app3.id)

        assert app1.status == "accepted"
        assert app2.status == "rejected"
        assert app3.status == "rejected"

    def test_application_count_after_rejections(self) -> None:
        """Rejected applications still count toward the total."""
        for _ in range(10):
            actor_id = self._make_actor_id()
            app = self.store.apply(self.project.id, actor_id)
            self.store.reject_application(app.id)

        # All 10 rejected apps still count
        assert self.store.get_application_count(self.project.id) == 10

    def test_multiple_seats_from_multiple_accepts(self) -> None:
        """A can accept multiple applicants, each gets their own seat."""
        b1 = self._make_actor_id()
        b2 = self._make_actor_id()

        app1 = self.store.apply(self.project.id, b1)
        app2 = self.store.apply(self.project.id, b2)

        seat1 = self.store.accept_application(app1.id)
        seat2 = self.store.accept_application(app2.id)

        assert seat1.actor_id == b1
        assert seat2.actor_id == b2
        assert len(self.store.seats) == 2
