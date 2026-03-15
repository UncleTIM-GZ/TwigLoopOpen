"""Admin service — read-only listing + freeze/hide operations."""

import uuid

from shared_schemas import PaginatedMeta
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.account import Account
from app.models.actor import Actor
from app.models.application import ProjectApplication
from app.models.project import Project
from app.schemas.admin import (
    AdminApplicationResponse,
    AdminProjectResponse,
    AdminUserResponse,
)


class AdminService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_users(
        self, page: int, limit: int
    ) -> tuple[list[AdminUserResponse], PaginatedMeta]:
        offset = (page - 1) * limit

        stmt = (
            select(Account, Actor)
            .outerjoin(Actor, Account.id == Actor.account_id)
            .order_by(Account.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        count_stmt = select(func.count()).select_from(Account)

        result = await self._session.execute(stmt)
        rows = result.all()
        total = (await self._session.execute(count_stmt)).scalar_one()

        items = [
            AdminUserResponse(
                account_id=account.id,
                email=account.email,
                account_status=account.status,
                actor_id=actor.id if actor else None,
                display_name=actor.display_name if actor else None,
                created_at=account.created_at,
            )
            for account, actor in rows
        ]

        meta = PaginatedMeta(total=total, page=page, limit=limit, has_next=(offset + limit) < total)
        return items, meta

    async def list_projects(
        self, page: int, limit: int
    ) -> tuple[list[AdminProjectResponse], PaginatedMeta]:
        offset = (page - 1) * limit

        stmt = select(Project).order_by(Project.created_at.desc()).offset(offset).limit(limit)
        count_stmt = select(func.count()).select_from(Project)

        result = await self._session.execute(stmt)
        items_raw = list(result.scalars().all())
        total = (await self._session.execute(count_stmt)).scalar_one()

        items = [
            AdminProjectResponse(
                project_id=p.id,
                title=p.title,
                project_type=p.project_type,
                status=p.status,
                founder_actor_id=p.founder_actor_id,
                created_at=p.created_at,
            )
            for p in items_raw
        ]

        meta = PaginatedMeta(total=total, page=page, limit=limit, has_next=(offset + limit) < total)
        return items, meta

    async def list_applications(
        self, page: int, limit: int
    ) -> tuple[list[AdminApplicationResponse], PaginatedMeta]:
        offset = (page - 1) * limit

        stmt = (
            select(ProjectApplication)
            .order_by(ProjectApplication.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        count_stmt = select(func.count()).select_from(ProjectApplication)

        result = await self._session.execute(stmt)
        items_raw = list(result.scalars().all())
        total = (await self._session.execute(count_stmt)).scalar_one()

        items = [
            AdminApplicationResponse(
                application_id=a.id,
                project_id=a.project_id,
                actor_id=a.actor_id,
                status=a.status,
                intended_role=a.intended_role,
                created_at=a.created_at,
            )
            for a in items_raw
        ]

        meta = PaginatedMeta(total=total, page=page, limit=limit, has_next=(offset + limit) < total)
        return items, meta

    async def freeze_user(self, actor_id: uuid.UUID) -> AdminUserResponse:
        stmt = select(Actor).where(Actor.id == actor_id)
        result = await self._session.execute(stmt)
        actor = result.scalar_one_or_none()
        if not actor:
            raise NotFoundError("Actor not found")

        stmt_acc = select(Account).where(Account.id == actor.account_id)
        result_acc = await self._session.execute(stmt_acc)
        account = result_acc.scalar_one_or_none()
        if not account:
            raise NotFoundError("Account not found")

        account.status = "frozen"
        await self._session.flush()
        await self._session.refresh(account)

        return AdminUserResponse(
            account_id=account.id,
            email=account.email,
            account_status=account.status,
            actor_id=actor.id,
            display_name=actor.display_name,
            created_at=account.created_at,
        )

    async def hide_project(self, project_id: uuid.UUID) -> AdminProjectResponse:
        stmt = select(Project).where(Project.id == project_id)
        result = await self._session.execute(stmt)
        project = result.scalar_one_or_none()
        if not project:
            raise NotFoundError("Project not found")

        project.status = "hidden"
        await self._session.flush()
        await self._session.refresh(project)

        return AdminProjectResponse(
            project_id=project.id,
            title=project.title,
            project_type=project.project_type,
            status=project.status,
            founder_actor_id=project.founder_actor_id,
            created_at=project.created_at,
        )
