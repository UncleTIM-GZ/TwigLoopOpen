"""Project fixtures — general, public_benefit, recruitment, and limit scenarios."""

from datetime import UTC, datetime

import pytest

from app.models.project import Project
from app.models.work_package import WorkPackage


def _make_project(
    *,
    founder_actor_id,
    project_type: str = "general",
    title: str = "Test Project",
    summary: str = "A test project for unit tests.",
    status: str = "draft",
    needs_human_reviewer: bool = False,
    human_review_status: str = "none",
    has_reward: bool = False,
    has_sponsor: bool = False,
    created_via: str = "web",
) -> Project:
    """Build a Project instance without persisting."""
    project = Project(
        founder_actor_id=founder_actor_id,
        project_type=project_type,
        founder_type="ordinary",
        title=title,
        summary=summary,
        target_users="developers",
        current_stage="idea",
        status=status,
        needs_human_reviewer=needs_human_reviewer,
        human_review_status=human_review_status,
        has_reward=has_reward,
        has_sponsor=has_sponsor,
        created_via=created_via,
    )
    now = datetime(2026, 3, 15, 12, 0, 0, tzinfo=UTC)
    project.created_at = now
    project.updated_at = now
    return project


# ── General project ─────────────────────────────────────────────────────


@pytest.fixture
async def general_project(session, founder_actor) -> Project:
    project = _make_project(
        founder_actor_id=founder_actor.id,
        project_type="general",
        title="General Test Project",
    )
    session.add(project)
    await session.flush()
    return project


# ── Public benefit project (needs human reviewer) ───────────────────────


@pytest.fixture
async def public_benefit_project(session, founder_actor) -> Project:
    project = _make_project(
        founder_actor_id=founder_actor.id,
        project_type="public_benefit",
        title="Public Benefit Test Project",
        needs_human_reviewer=True,
        human_review_status="reviewer_required",
    )
    session.add(project)
    await session.flush()
    return project


# ── Recruitment project (has reward) ────────────────────────────────────


@pytest.fixture
async def recruitment_project(session, founder_actor) -> Project:
    project = _make_project(
        founder_actor_id=founder_actor.id,
        project_type="recruitment",
        title="Recruitment Test Project",
        has_reward=True,
    )
    session.add(project)
    await session.flush()
    return project


# ── Project with 5 work packages (at limit) ─────────────────────────────


@pytest.fixture
async def project_with_5_wps(session, founder_actor) -> tuple[Project, list[WorkPackage]]:
    project = _make_project(
        founder_actor_id=founder_actor.id,
        title="Project With 5 WPs",
    )
    session.add(project)
    await session.flush()

    wps = []
    for i in range(5):
        wp = WorkPackage(
            project_id=project.id,
            title=f"Work Package {i + 1}",
            description=f"Description for WP {i + 1}",
            status="draft",
            sort_order=i,
        )
        now = datetime(2026, 3, 15, 12, 0, 0, tzinfo=UTC)
        wp.created_at = now
        wp.updated_at = now
        session.add(wp)
        wps.append(wp)
    await session.flush()
    return project, wps


# ── Project with 20 tasks (at limit) ────────────────────────────────────


@pytest.fixture
async def project_with_20_tasks(session, founder_actor):
    """Return (project, work_package, [20 task_cards])."""
    from app.models.task_card import TaskCard

    project = _make_project(
        founder_actor_id=founder_actor.id,
        title="Project With 20 Tasks",
    )
    session.add(project)
    await session.flush()

    wp = WorkPackage(
        project_id=project.id,
        title="Big WP",
        status="draft",
        sort_order=0,
    )
    now = datetime(2026, 3, 15, 12, 0, 0, tzinfo=UTC)
    wp.created_at = now
    wp.updated_at = now
    session.add(wp)
    await session.flush()

    tasks = []
    for i in range(20):
        task = TaskCard(
            work_package_id=wp.id,
            title=f"Task {i + 1}",
            task_type="development",
            goal=f"Goal {i + 1}",
            output_spec=f"Output {i + 1}",
            completion_criteria=f"Criteria {i + 1}",
            main_role="developer",
            risk_level="low",
            status="draft",
            ewu=4,
        )
        task.created_at = now
        task.updated_at = now
        session.add(task)
        tasks.append(task)
    await session.flush()
    return project, wp, tasks
