"""Factory shortcut functions for creating test entities in the database.

These are imperative helpers (not pytest fixtures) so tests can create
entities inline with custom parameters.
"""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.actor import Actor
from app.models.application import ProjectApplication
from app.models.project import Project
from app.models.task_card import TaskCard
from app.models.work_package import WorkPackage

_NOW = datetime(2026, 3, 15, 12, 0, 0, tzinfo=UTC)


async def create_account(
    session: AsyncSession,
    *,
    email: str = "factory@twigloop.test",
) -> Account:
    """Create and persist an Account."""
    account = Account(
        email=email,
        password_hash="$2b$12$fakehash",
        auth_method="password",
        registration_source="web",
        status="active",
    )
    account.created_at = _NOW
    account.updated_at = _NOW
    session.add(account)
    await session.flush()
    return account


async def create_actor(
    session: AsyncSession,
    *,
    account_id: uuid.UUID,
    display_name: str = "Factory User",
    is_founder: bool = False,
    is_collaborator: bool = False,
    is_reviewer: bool = False,
    is_sponsor: bool = False,
) -> Actor:
    """Create and persist an Actor."""
    actor = Actor(
        account_id=account_id,
        display_name=display_name,
        actor_type="human",
        is_founder=is_founder,
        is_collaborator=is_collaborator,
        is_reviewer=is_reviewer,
        is_sponsor=is_sponsor,
        profile_status="profile_complete",
        level="L0",
    )
    actor.created_at = _NOW
    actor.updated_at = _NOW
    session.add(actor)
    await session.flush()
    return actor


async def create_project(
    session: AsyncSession,
    *,
    founder_actor_id: uuid.UUID,
    project_type: str = "general",
    title: str = "Factory Project",
    summary: str = "Created by factory",
    status: str = "draft",
    needs_human_reviewer: bool = False,
    has_reward: bool = False,
) -> Project:
    """Create and persist a Project."""
    human_review_status = "reviewer_required" if needs_human_reviewer else "none"
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
        has_sponsor=False,
        created_via="web",
    )
    project.created_at = _NOW
    project.updated_at = _NOW
    session.add(project)
    await session.flush()
    return project


async def create_work_package(
    session: AsyncSession,
    *,
    project_id: uuid.UUID,
    title: str = "Factory WP",
    sort_order: int = 0,
) -> WorkPackage:
    """Create and persist a WorkPackage."""
    wp = WorkPackage(
        project_id=project_id,
        title=title,
        description="Factory work package",
        status="draft",
        sort_order=sort_order,
    )
    wp.created_at = _NOW
    wp.updated_at = _NOW
    session.add(wp)
    await session.flush()
    return wp


async def create_task(
    session: AsyncSession,
    *,
    work_package_id: uuid.UUID,
    title: str = "Factory Task",
    task_type: str = "development",
    ewu: Decimal = Decimal("4.00"),
    status: str = "draft",
) -> TaskCard:
    """Create and persist a TaskCard."""
    task = TaskCard(
        work_package_id=work_package_id,
        title=title,
        task_type=task_type,
        goal="Factory goal",
        output_spec="Factory output",
        completion_criteria="Factory criteria",
        main_role="developer",
        risk_level="low",
        status=status,
        ewu=ewu,
    )
    task.created_at = _NOW
    task.updated_at = _NOW
    session.add(task)
    await session.flush()
    return task


async def create_application(
    session: AsyncSession,
    *,
    project_id: uuid.UUID,
    actor_id: uuid.UUID,
    seat_preference: str = "growth",
    intended_role: str = "developer",
    status: str = "submitted",
) -> ProjectApplication:
    """Create and persist a ProjectApplication."""
    app = ProjectApplication(
        project_id=project_id,
        actor_id=actor_id,
        seat_preference=seat_preference,
        intended_role=intended_role,
        motivation="Factory motivation",
        availability="10h/week",
        status=status,
    )
    app.created_at = _NOW
    app.updated_at = _NOW
    session.add(app)
    await session.flush()
    return app
