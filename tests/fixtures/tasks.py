"""Task card fixtures — normal, max EWU, and over-EWU scenarios."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.models.task_card import TaskCard
from app.models.work_package import WorkPackage


def _make_work_package(project_id, *, title: str = "Test WP", sort_order: int = 0) -> WorkPackage:
    """Build a WorkPackage instance without persisting."""
    wp = WorkPackage(
        project_id=project_id,
        title=title,
        description="Test work package",
        status="draft",
        sort_order=sort_order,
    )
    now = datetime(2026, 3, 15, 12, 0, 0, tzinfo=UTC)
    wp.created_at = now
    wp.updated_at = now
    return wp


def _make_task(
    work_package_id,
    *,
    title: str = "Test Task",
    task_type: str = "development",
    ewu: Decimal = Decimal("4.00"),
    status: str = "draft",
) -> TaskCard:
    """Build a TaskCard instance without persisting."""
    task = TaskCard(
        work_package_id=work_package_id,
        title=title,
        task_type=task_type,
        goal="Test goal",
        output_spec="Test output spec",
        completion_criteria="Test completion criteria",
        main_role="developer",
        risk_level="low",
        status=status,
        ewu=ewu,
    )
    now = datetime(2026, 3, 15, 12, 0, 0, tzinfo=UTC)
    task.created_at = now
    task.updated_at = now
    return task


@pytest.fixture
async def work_package(session, general_project) -> WorkPackage:
    """A single work package belonging to general_project."""
    wp = _make_work_package(general_project.id)
    session.add(wp)
    await session.flush()
    return wp


# ── Normal task (EWU = 4) ────────────────────────────────────────────────


@pytest.fixture
async def normal_task(session, work_package) -> TaskCard:
    task = _make_task(work_package.id, title="Normal Task", ewu=Decimal("4.00"))
    session.add(task)
    await session.flush()
    return task


# ── Max EWU task (EWU = 8) ──────────────────────────────────────────────


@pytest.fixture
async def max_ewu_task(session, work_package) -> TaskCard:
    task = _make_task(work_package.id, title="Max EWU Task", ewu=Decimal("8.00"))
    session.add(task)
    await session.flush()
    return task


# ── Over EWU task (EWU = 9, should be rejected by validation) ────────────


@pytest.fixture
async def over_ewu_task(session, work_package) -> TaskCard:
    task = _make_task(work_package.id, title="Over EWU Task", ewu=Decimal("9.00"))
    session.add(task)
    await session.flush()
    return task
