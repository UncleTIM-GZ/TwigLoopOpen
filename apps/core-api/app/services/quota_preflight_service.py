"""Quota preflight service — validates platform quota rules before writes."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.models.application import ProjectApplication
from app.models.project import Project
from app.models.seat import ProjectSeat
from app.models.task_card import TaskCard
from app.models.work_package import WorkPackage


@dataclass
class QuotaViolation:
    """Structured rule violation result."""

    rule_code: str
    severity: str  # "error" | "warning"
    object_scope: str
    current_value: int | float
    max_allowed: int | float
    message: str
    recommended_next_action: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_code": self.rule_code,
            "severity": self.severity,
            "object_scope": self.object_scope,
            "current_value": self.current_value,
            "max_allowed": self.max_allowed,
            "message": self.message,
            "recommended_next_action": self.recommended_next_action,
        }


class QuotaPreflightService:
    """Validate platform quota rules against current DB state."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def check_project_quota(
        self,
        draft_id_or_fields: dict[str, Any],
        actor_id: UUID,
    ) -> list[QuotaViolation]:
        """Check all project-level quotas.

        Args:
            draft_id_or_fields: Dict containing work_packages and tasks data
                to validate. May include nested structure or counts.
            actor_id: The founder's actor UUID.
        """
        violations: list[QuotaViolation] = []

        # Extract counts from draft fields
        work_packages = draft_id_or_fields.get("work_packages", [])
        wp_count = len(work_packages)
        total_tasks = 0
        for wp in work_packages:
            tasks = wp.get("tasks", [])
            task_count = len(tasks)
            total_tasks += task_count

            # Rule 2: Tasks per WP <= 6
            if task_count > MAX_TASKS_PER_WORK_PACKAGE:
                violations.append(
                    QuotaViolation(
                        rule_code="TASKS_PER_WP",
                        severity="error",
                        object_scope=f"work_package:{wp.get('title', '?')}",
                        current_value=task_count,
                        max_allowed=MAX_TASKS_PER_WORK_PACKAGE,
                        message=(
                            f"Work package '{wp.get('title', '?')}' has "
                            f"{task_count} tasks (max {MAX_TASKS_PER_WORK_PACKAGE})"
                        ),
                        recommended_next_action="Split into multiple work packages",
                    )
                )

            # Rule 4: EWU per task <= 8
            for task in tasks:
                ewu = task.get("ewu", 0)
                if isinstance(ewu, str):
                    ewu = float(ewu)
                if isinstance(ewu, Decimal):
                    ewu = float(ewu)
                if ewu > MAX_EWU_PER_TASK:
                    violations.append(
                        QuotaViolation(
                            rule_code="EWU_PER_TASK",
                            severity="error",
                            object_scope=f"task:{task.get('title', '?')}",
                            current_value=ewu,
                            max_allowed=MAX_EWU_PER_TASK,
                            message=(
                                f"Task '{task.get('title', '?')}' EWU is "
                                f"{ewu} (max {MAX_EWU_PER_TASK})"
                            ),
                            recommended_next_action=(
                                "Reduce task scope or split into smaller tasks"
                            ),
                        )
                    )

        # Rule 1: Work packages count <= 5
        if wp_count > MAX_WORK_PACKAGES_PER_PROJECT:
            violations.append(
                QuotaViolation(
                    rule_code="WP_PER_PROJECT",
                    severity="error",
                    object_scope="project",
                    current_value=wp_count,
                    max_allowed=MAX_WORK_PACKAGES_PER_PROJECT,
                    message=(
                        f"Project has {wp_count} work packages "
                        f"(max {MAX_WORK_PACKAGES_PER_PROJECT})"
                    ),
                    recommended_next_action="Merge related work packages",
                )
            )

        # Rule 3: Total tasks <= 20
        if total_tasks > MAX_TASKS_PER_PROJECT:
            violations.append(
                QuotaViolation(
                    rule_code="TASKS_PER_PROJECT",
                    severity="error",
                    object_scope="project",
                    current_value=total_tasks,
                    max_allowed=MAX_TASKS_PER_PROJECT,
                    message=(
                        f"Project has {total_tasks} total tasks (max {MAX_TASKS_PER_PROJECT})"
                    ),
                    recommended_next_action="Remove low-priority tasks",
                )
            )

        # Rule 5: Founder active projects <= 2 (allow exactly MAX, block above)
        active_projects = await self._count_active_projects(actor_id)
        if active_projects > MAX_ACTIVE_PROJECTS_NEW_FOUNDER:
            violations.append(
                QuotaViolation(
                    rule_code="ACTIVE_PROJECTS",
                    severity="error",
                    object_scope="founder",
                    current_value=active_projects,
                    max_allowed=MAX_ACTIVE_PROJECTS_NEW_FOUNDER,
                    message=(
                        f"Founder has {active_projects} active projects "
                        f"(max {MAX_ACTIVE_PROJECTS_NEW_FOUNDER})"
                    ),
                    recommended_next_action=("Complete or archive an existing project first"),
                )
            )

        # Rule 6: Founder open seats <= 12
        open_seats = await self._count_open_seats(actor_id)
        if open_seats > MAX_OPEN_SEATS_DEFAULT:
            violations.append(
                QuotaViolation(
                    rule_code="OPEN_SEATS",
                    severity="warning",
                    object_scope="founder",
                    current_value=open_seats,
                    max_allowed=MAX_OPEN_SEATS_DEFAULT,
                    message=(f"Founder has {open_seats} open seats (max {MAX_OPEN_SEATS_DEFAULT})"),
                    recommended_next_action="Fill or close existing seats first",
                )
            )

        # Rule 7: Founder active tasks <= 30
        active_tasks = await self._count_active_tasks(actor_id)
        if active_tasks > MAX_ACTIVE_TASKS_DEFAULT:
            violations.append(
                QuotaViolation(
                    rule_code="ACTIVE_TASKS",
                    severity="warning",
                    object_scope="founder",
                    current_value=active_tasks,
                    max_allowed=MAX_ACTIVE_TASKS_DEFAULT,
                    message=(
                        f"Founder has {active_tasks} active tasks (max {MAX_ACTIVE_TASKS_DEFAULT})"
                    ),
                    recommended_next_action="Complete existing tasks before adding more",
                )
            )

        return violations

    async def check_application_quota(
        self,
        project_id: UUID,
        task_id: UUID | None = None,
    ) -> list[QuotaViolation]:
        """Check application relationship limits.

        Args:
            project_id: The project UUID.
            task_id: Optional task UUID for per-task check.
        """
        violations: list[QuotaViolation] = []

        # Rule 1: Pending apps per project <= 30
        pending_project = await self._count_pending_applications_for_project(project_id)
        if pending_project > MAX_PENDING_APPLICATIONS_PER_PROJECT:
            violations.append(
                QuotaViolation(
                    rule_code="PENDING_APPS_PROJECT",
                    severity="error",
                    object_scope=f"project:{project_id}",
                    current_value=pending_project,
                    max_allowed=MAX_PENDING_APPLICATIONS_PER_PROJECT,
                    message=(
                        f"Project has {pending_project} pending applications "
                        f"(max {MAX_PENDING_APPLICATIONS_PER_PROJECT})"
                    ),
                    recommended_next_action="Review existing applications first",
                )
            )

        # Rule 2: Pending apps per task <= 10
        # Note: ProjectApplication currently does not have a task_id column.
        # When task-level applications are added, enable this check.
        if task_id is not None:
            pending_task = await self._count_pending_applications_for_task(task_id)
            if pending_task > MAX_PENDING_APPLICATIONS_PER_TASK:
                violations.append(
                    QuotaViolation(
                        rule_code="PENDING_APPS_TASK",
                        severity="error",
                        object_scope=f"task:{task_id}",
                        current_value=pending_task,
                        max_allowed=MAX_PENDING_APPLICATIONS_PER_TASK,
                        message=(
                            f"Task has {pending_task} pending applications "
                            f"(max {MAX_PENDING_APPLICATIONS_PER_TASK})"
                        ),
                        recommended_next_action="Review existing task applications first",
                    )
                )

        return violations

    # ---- counting helpers ----

    async def _count_active_projects(self, actor_id: UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Project)
            .where(
                Project.founder_actor_id == actor_id,
                Project.status.in_(ACTIVE_PROJECT_STATUSES),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def _count_open_seats(self, actor_id: UUID) -> int:
        """Count seats in open statuses across all the founder's projects."""
        stmt = (
            select(func.count())
            .select_from(ProjectSeat)
            .join(Project, ProjectSeat.project_id == Project.id)
            .where(
                Project.founder_actor_id == actor_id,
                ProjectSeat.status.in_(OPEN_SEAT_STATUSES),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def _count_active_tasks(self, actor_id: UUID) -> int:
        """Count tasks in active statuses across all the founder's projects."""
        stmt = (
            select(func.count())
            .select_from(TaskCard)
            .join(WorkPackage, TaskCard.work_package_id == WorkPackage.id)
            .join(Project, WorkPackage.project_id == Project.id)
            .where(
                Project.founder_actor_id == actor_id,
                TaskCard.status.in_(ACTIVE_TASK_STATUSES),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def _count_pending_applications_for_project(self, project_id: UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(ProjectApplication)
            .where(
                ProjectApplication.project_id == project_id,
                ProjectApplication.status.in_(PENDING_APPLICATION_STATUSES),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def _count_pending_applications_for_task(self, task_id: UUID) -> int:
        """Count pending applications for a specific task.

        Note: The current ProjectApplication model has no task_id column.
        Returns 0 until task-level applications are supported.
        """
        # TODO: Enable when ProjectApplication gains a task_id FK
        _ = task_id
        return 0
