"""Quota & complexity gate enforcement tests.

Layer 6 from the test plan — all 24 quota test cases.
Tests the resource limits: WP per project, tasks per WP, total tasks,
EWU range, active projects per founder, applications per project.

These are integration-level tests that describe the EXPECTED flow.
They use mock session/data since we don't have a real DB in CI yet.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Quota constants (MVP limits)
# ---------------------------------------------------------------------------

MAX_WP_PER_PROJECT = 5
MAX_TASKS_PER_WP = 6
MAX_TASKS_PER_PROJECT = 20
MAX_EWU_PER_TASK = Decimal("8.0")
MIN_EWU_PER_TASK = Decimal("0.5")
MAX_ACTIVE_PROJECTS_PER_FOUNDER = 2
MAX_APPLICATIONS_PER_PROJECT = 30


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class QuotaExceededError(Exception):
    """Raised when a resource quota is exceeded."""


class ValidationError(Exception):
    """Raised when a field value is invalid."""


# ---------------------------------------------------------------------------
# In-memory quota-aware store
# ---------------------------------------------------------------------------


@dataclass
class QuotaProject:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    founder_actor_id: str = ""
    title: str = "Quota Test Project"
    status: str = "draft"


@dataclass
class QuotaWorkPackage:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    title: str = "Quota WP"
    status: str = "draft"


@dataclass
class QuotaTask:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    work_package_id: str = ""
    project_id: str = ""
    title: str = "Quota Task"
    ewu: Decimal = field(default_factory=lambda: Decimal("2.0"))
    status: str = "draft"


class QuotaStore:
    """In-memory store that enforces all MVP quota rules."""

    def __init__(self) -> None:
        self.projects: dict[str, QuotaProject] = {}
        self.work_packages: dict[str, QuotaWorkPackage] = {}
        self.tasks: dict[str, QuotaTask] = {}

    # -- Project management --

    def count_active_projects(self, founder_id: str) -> int:
        return sum(
            1
            for p in self.projects.values()
            if p.founder_actor_id == founder_id and p.status not in ("closed",)
        )

    def create_project(self, founder_id: str, **kwargs: Any) -> QuotaProject:
        active = self.count_active_projects(founder_id)
        if active >= MAX_ACTIVE_PROJECTS_PER_FOUNDER:
            raise QuotaExceededError(
                f"Founder has {active} active projects, maximum is "
                f"{MAX_ACTIVE_PROJECTS_PER_FOUNDER}"
            )
        project = QuotaProject(founder_actor_id=founder_id, **kwargs)
        self.projects[project.id] = project
        return project

    def close_project(self, project_id: str) -> None:
        self.projects[project_id].status = "closed"

    # -- Work package management --

    def count_wps(self, project_id: str) -> int:
        return sum(
            1 for wp in self.work_packages.values() if wp.project_id == project_id
        )

    def create_wp(self, project_id: str, **kwargs: Any) -> QuotaWorkPackage:
        count = self.count_wps(project_id)
        if count >= MAX_WP_PER_PROJECT:
            raise QuotaExceededError(
                f"Project has {count} work packages, maximum is {MAX_WP_PER_PROJECT}"
            )
        wp = QuotaWorkPackage(project_id=project_id, **kwargs)
        self.work_packages[wp.id] = wp
        return wp

    def delete_wp(self, wp_id: str) -> None:
        del self.work_packages[wp_id]

    # -- Task management --

    def count_tasks_in_wp(self, wp_id: str) -> int:
        return sum(
            1 for t in self.tasks.values() if t.work_package_id == wp_id
        )

    def count_tasks_in_project(self, project_id: str) -> int:
        return sum(
            1
            for t in self.tasks.values()
            if t.project_id == project_id and t.status != "closed"
        )

    def create_task(
        self, wp_id: str, project_id: str, ewu: Decimal | float | int = 2, **kwargs: Any
    ) -> QuotaTask:
        # Validate EWU
        try:
            ewu_decimal = Decimal(str(ewu))
        except (InvalidOperation, ValueError) as exc:
            raise ValidationError(f"Invalid EWU value: {ewu}") from exc

        if ewu_decimal < MIN_EWU_PER_TASK:
            raise ValidationError(
                f"EWU {ewu_decimal} is below minimum {MIN_EWU_PER_TASK}"
            )
        if ewu_decimal > MAX_EWU_PER_TASK:
            raise QuotaExceededError(
                f"EWU {ewu_decimal} exceeds maximum {MAX_EWU_PER_TASK}"
            )

        # Check per-WP limit
        wp_count = self.count_tasks_in_wp(wp_id)
        if wp_count >= MAX_TASKS_PER_WP:
            raise QuotaExceededError(
                f"Work package has {wp_count} tasks, maximum is {MAX_TASKS_PER_WP}"
            )

        # Check per-project limit
        project_count = self.count_tasks_in_project(project_id)
        if project_count >= MAX_TASKS_PER_PROJECT:
            raise QuotaExceededError(
                f"Project has {project_count} tasks, maximum is {MAX_TASKS_PER_PROJECT}"
            )

        task = QuotaTask(
            work_package_id=wp_id,
            project_id=project_id,
            ewu=ewu_decimal,
            **kwargs,
        )
        self.tasks[task.id] = task
        return task

    def close_task(self, task_id: str) -> None:
        self.tasks[task_id].status = "closed"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestWPLimitPerProject:
    """QT-001 ~ QT-004: Work package limit (5 per project)."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.store = QuotaStore()
        self.founder_id = str(uuid.uuid4())
        self.project = self.store.create_project(self.founder_id)

    def test_wp_limit_1_allowed(self) -> None:
        """QT-001: Creating the first WP succeeds."""
        wp = self.store.create_wp(self.project.id)
        assert wp.project_id == self.project.id

    def test_wp_limit_5_allowed(self) -> None:
        """QT-002: Creating the 5th WP succeeds."""
        for i in range(4):
            self.store.create_wp(self.project.id, title=f"WP {i + 1}")
        wp5 = self.store.create_wp(self.project.id, title="WP 5")

        assert self.store.count_wps(self.project.id) == 5
        assert wp5.title == "WP 5"

    def test_wp_limit_6_blocked(self) -> None:
        """QT-003: Creating the 6th WP is blocked."""
        for i in range(5):
            self.store.create_wp(self.project.id, title=f"WP {i + 1}")

        with pytest.raises(QuotaExceededError, match="maximum is 5"):
            self.store.create_wp(self.project.id, title="WP 6")

    def test_wp_delete_then_recreate(self) -> None:
        """QT-004: After deleting a WP, a new one can be created."""
        wps = []
        for i in range(5):
            wps.append(self.store.create_wp(self.project.id, title=f"WP {i + 1}"))

        self.store.delete_wp(wps[0].id)
        assert self.store.count_wps(self.project.id) == 4

        new_wp = self.store.create_wp(self.project.id, title="WP Replacement")
        assert self.store.count_wps(self.project.id) == 5
        assert new_wp.title == "WP Replacement"


class TestTaskLimitPerWP:
    """QT-005 ~ QT-008: Task limit (6 per work package)."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.store = QuotaStore()
        self.founder_id = str(uuid.uuid4())
        self.project = self.store.create_project(self.founder_id)
        self.wp = self.store.create_wp(self.project.id)

    def test_tasks_per_wp_1_allowed(self) -> None:
        """QT-005: Creating the first task in a WP succeeds."""
        task = self.store.create_task(self.wp.id, self.project.id)
        assert task.work_package_id == self.wp.id

    def test_tasks_per_wp_6_allowed(self) -> None:
        """QT-006: Creating the 6th task in a WP succeeds."""
        for i in range(5):
            self.store.create_task(self.wp.id, self.project.id, title=f"Task {i + 1}")
        task6 = self.store.create_task(self.wp.id, self.project.id, title="Task 6")

        assert self.store.count_tasks_in_wp(self.wp.id) == 6
        assert task6.title == "Task 6"

    def test_tasks_per_wp_7_blocked(self) -> None:
        """QT-007: Creating the 7th task in a WP is blocked."""
        for i in range(6):
            self.store.create_task(self.wp.id, self.project.id, title=f"Task {i + 1}")

        with pytest.raises(QuotaExceededError, match="maximum is 6"):
            self.store.create_task(self.wp.id, self.project.id, title="Task 7")

    def test_different_wps_independent_count(self) -> None:
        """QT-008: Different WPs have independent task counts."""
        wp2 = self.store.create_wp(self.project.id, title="WP 2")

        # Fill WP1 to limit
        for i in range(6):
            self.store.create_task(self.wp.id, self.project.id, title=f"WP1-Task-{i}")

        # WP2 can still accept tasks
        task = self.store.create_task(wp2.id, self.project.id, title="WP2-Task-1")
        assert task.work_package_id == wp2.id


class TestTotalTasksPerProject:
    """QT-009 ~ QT-012: Total task limit (20 per project)."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.store = QuotaStore()
        self.founder_id = str(uuid.uuid4())
        self.project = self.store.create_project(self.founder_id)

    def _create_tasks(self, count: int) -> list[QuotaTask]:
        """Helper to create multiple tasks across WPs (up to 6 per WP)."""
        tasks: list[QuotaTask] = []
        wp_index = 0
        wp = self.store.create_wp(self.project.id, title=f"WP {wp_index}")
        for i in range(count):
            if self.store.count_tasks_in_wp(wp.id) >= MAX_TASKS_PER_WP:
                wp_index += 1
                wp = self.store.create_wp(self.project.id, title=f"WP {wp_index}")
            task = self.store.create_task(
                wp.id, self.project.id, title=f"Task {i + 1}"
            )
            tasks.append(task)
        return tasks

    def test_total_tasks_20_allowed(self) -> None:
        """QT-009/QT-010: Creating up to 20 tasks succeeds."""
        tasks = self._create_tasks(20)
        assert len(tasks) == 20
        assert self.store.count_tasks_in_project(self.project.id) == 20

    def test_total_tasks_21_blocked(self) -> None:
        """QT-010: Creating the 21st task is blocked."""
        self._create_tasks(20)

        # Need a new WP since existing ones might be full
        extra_wp = self.store.create_wp(self.project.id, title="Extra WP")
        with pytest.raises(QuotaExceededError, match="maximum is 20"):
            self.store.create_task(extra_wp.id, self.project.id, title="Task 21")

    def test_cross_wp_total_count(self) -> None:
        """QT-011: Tasks across multiple WPs are counted together."""
        wp1 = self.store.create_wp(self.project.id, title="WP 1")
        wp2 = self.store.create_wp(self.project.id, title="WP 2")

        # 6 tasks in each WP = 12 total
        for i in range(6):
            self.store.create_task(wp1.id, self.project.id, title=f"WP1-T{i}")
        for i in range(6):
            self.store.create_task(wp2.id, self.project.id, title=f"WP2-T{i}")

        assert self.store.count_tasks_in_project(self.project.id) == 12

    def test_closed_tasks_not_counted(self) -> None:
        """QT-012: Closed tasks don't count toward the project total."""
        tasks = self._create_tasks(20)
        assert self.store.count_tasks_in_project(self.project.id) == 20

        # Close one task
        self.store.close_task(tasks[0].id)
        assert self.store.count_tasks_in_project(self.project.id) == 19

        # Now we can create one more
        wp = self.store.create_wp(self.project.id, title="Recovery WP")
        new_task = self.store.create_task(wp.id, self.project.id, title="Recovery Task")
        assert new_task.title == "Recovery Task"


class TestEWURange:
    """QT-013 ~ QT-018: EWU validation (0.5 ~ 8 per task)."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.store = QuotaStore()
        self.founder_id = str(uuid.uuid4())
        self.project = self.store.create_project(self.founder_id)
        self.wp = self.store.create_wp(self.project.id)

    def test_ewu_1_allowed(self) -> None:
        """QT-013: EWU = 1 is valid."""
        task = self.store.create_task(self.wp.id, self.project.id, ewu=1)
        assert task.ewu == Decimal("1")

    def test_ewu_8_allowed(self) -> None:
        """QT-014: EWU = 8 (maximum) is valid."""
        task = self.store.create_task(self.wp.id, self.project.id, ewu=8)
        assert task.ewu == Decimal("8")

    def test_ewu_9_blocked(self) -> None:
        """QT-015: EWU = 9 exceeds maximum and is blocked."""
        with pytest.raises(QuotaExceededError, match="exceeds maximum"):
            self.store.create_task(self.wp.id, self.project.id, ewu=9)

    def test_ewu_0_blocked(self) -> None:
        """QT-016: EWU = 0 is below minimum and is blocked."""
        with pytest.raises(ValidationError, match="below minimum"):
            self.store.create_task(self.wp.id, self.project.id, ewu=0)

    def test_ewu_half_allowed(self) -> None:
        """QT-017: EWU = 0.5 (minimum) is valid."""
        task = self.store.create_task(self.wp.id, self.project.id, ewu=0.5)
        assert task.ewu == Decimal("0.5")

    def test_ewu_non_numeric_blocked(self) -> None:
        """QT-018: Non-numeric EWU is rejected."""
        with pytest.raises(ValidationError, match="Invalid EWU"):
            self.store.create_task(self.wp.id, self.project.id, ewu="abc")

    def test_ewu_negative_blocked(self) -> None:
        """EWU cannot be negative."""
        with pytest.raises(ValidationError, match="below minimum"):
            self.store.create_task(self.wp.id, self.project.id, ewu=-1)

    def test_ewu_decimal_precision(self) -> None:
        """EWU accepts decimal values with reasonable precision."""
        task = self.store.create_task(self.wp.id, self.project.id, ewu=3.5)
        assert task.ewu == Decimal("3.5")


class TestActiveProjectsPerFounder:
    """QT-019 ~ QT-022: Active project limit (2 per founder)."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.store = QuotaStore()
        self.founder_id = str(uuid.uuid4())

    def test_active_projects_1_allowed(self) -> None:
        """QT-019: First active project succeeds."""
        p = self.store.create_project(self.founder_id)
        assert p.founder_actor_id == self.founder_id

    def test_active_projects_2_allowed(self) -> None:
        """QT-020: Second active project succeeds."""
        self.store.create_project(self.founder_id, title="Project 1")
        p2 = self.store.create_project(self.founder_id, title="Project 2")

        assert self.store.count_active_projects(self.founder_id) == 2
        assert p2.title == "Project 2"

    def test_active_projects_3_blocked(self) -> None:
        """QT-021: Third active project is blocked."""
        self.store.create_project(self.founder_id, title="Project 1")
        self.store.create_project(self.founder_id, title="Project 2")

        with pytest.raises(QuotaExceededError, match="maximum is 2"):
            self.store.create_project(self.founder_id, title="Project 3")

    def test_close_then_create_allowed(self) -> None:
        """QT-022: After closing a project, a new one can be created."""
        p1 = self.store.create_project(self.founder_id, title="Project 1")
        self.store.create_project(self.founder_id, title="Project 2")

        self.store.close_project(p1.id)
        assert self.store.count_active_projects(self.founder_id) == 1

        p3 = self.store.create_project(self.founder_id, title="Project 3")
        assert p3.title == "Project 3"
        assert self.store.count_active_projects(self.founder_id) == 2

    def test_different_founders_independent(self) -> None:
        """Different founders have independent project limits."""
        other_founder = str(uuid.uuid4())

        self.store.create_project(self.founder_id, title="F1-P1")
        self.store.create_project(self.founder_id, title="F1-P2")

        # Other founder can still create projects
        p = self.store.create_project(other_founder, title="F2-P1")
        assert p.founder_actor_id == other_founder


class TestApplicationLimitPerProject:
    """QT-023 ~ QT-024: Application limit (30 per project)."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.store = QuotaStore()
        self.founder_id = str(uuid.uuid4())
        self.project = self.store.create_project(self.founder_id)
        self._applications: list[dict[str, str]] = []
        self._app_counter = 0

    def _apply(self) -> dict[str, str]:
        """Submit one application to the project."""
        self._app_counter += 1
        actor_id = str(uuid.uuid4())
        count = len(self._applications)
        if count >= MAX_APPLICATIONS_PER_PROJECT:
            raise QuotaExceededError(
                f"Project has {count} applications, maximum is "
                f"{MAX_APPLICATIONS_PER_PROJECT}"
            )
        app = {"id": str(uuid.uuid4()), "actor_id": actor_id, "status": "submitted"}
        self._applications.append(app)
        return app

    def test_30_applications_allowed(self) -> None:
        """QT-023: 30 applications succeed."""
        for _ in range(30):
            app = self._apply()
            assert app["status"] == "submitted"
        assert len(self._applications) == 30

    def test_31st_application_blocked(self) -> None:
        """QT-024: 31st application is blocked."""
        for _ in range(30):
            self._apply()

        with pytest.raises(QuotaExceededError, match="maximum is 30"):
            self._apply()
