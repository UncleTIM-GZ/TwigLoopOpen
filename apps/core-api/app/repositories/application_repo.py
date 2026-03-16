"""Application repository."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import ProjectApplication


class ApplicationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, app_id: uuid.UUID) -> ProjectApplication | None:
        stmt = select(ProjectApplication).where(ProjectApplication.id == app_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id_for_update(self, app_id: uuid.UUID) -> ProjectApplication | None:
        """Lock the row for state change — prevents concurrent modifications."""
        stmt = select(ProjectApplication).where(ProjectApplication.id == app_id).with_for_update()
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_project(self, project_id: uuid.UUID) -> list[ProjectApplication]:
        stmt = (
            select(ProjectApplication)
            .where(ProjectApplication.project_id == project_id)
            .order_by(ProjectApplication.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_paginated_by_project(
        self, project_id: uuid.UUID, *, offset: int = 0, limit: int = 20
    ) -> tuple[list[ProjectApplication], int]:
        """Return (items, total_count) for applications in a project."""
        base_filter = ProjectApplication.project_id == project_id

        count_stmt = select(func.count()).select_from(ProjectApplication).where(base_filter)
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = (
            select(ProjectApplication)
            .where(base_filter)
            .order_by(ProjectApplication.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())
        return items, total

    async def find_existing(
        self, project_id: uuid.UUID, actor_id: uuid.UUID
    ) -> ProjectApplication | None:
        stmt = select(ProjectApplication).where(
            ProjectApplication.project_id == project_id,
            ProjectApplication.actor_id == actor_id,
            ProjectApplication.status.in_(["submitted", "under_review"]),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, app: ProjectApplication) -> ProjectApplication:
        self._session.add(app)
        await self._session.flush()
        return app

    async def update_fields(
        self, app: ProjectApplication, updates: dict[str, object]
    ) -> ProjectApplication:
        for key, value in updates.items():
            setattr(app, key, value)
        await self._session.flush()
        await self._session.refresh(app)
        return app
