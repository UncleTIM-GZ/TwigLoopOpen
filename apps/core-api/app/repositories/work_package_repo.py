"""Work package repository."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.work_package import WorkPackage


class WorkPackageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, wp_id: uuid.UUID) -> WorkPackage | None:
        stmt = select(WorkPackage).where(WorkPackage.id == wp_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_project(self, project_id: uuid.UUID) -> list[WorkPackage]:
        stmt = (
            select(WorkPackage)
            .where(WorkPackage.project_id == project_id)
            .order_by(WorkPackage.sort_order)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_paginated_by_project(
        self, project_id: uuid.UUID, *, offset: int = 0, limit: int = 20
    ) -> tuple[list[WorkPackage], int]:
        """Return (items, total_count) for work packages in a project."""
        base_filter = WorkPackage.project_id == project_id

        count_stmt = select(func.count()).select_from(WorkPackage).where(base_filter)
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = (
            select(WorkPackage)
            .where(base_filter)
            .order_by(WorkPackage.sort_order)
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())
        return items, total

    async def create(self, wp: WorkPackage) -> WorkPackage:
        self._session.add(wp)
        await self._session.flush()
        return wp

    async def update_fields(self, wp: WorkPackage, updates: dict[str, object]) -> WorkPackage:
        for key, value in updates.items():
            setattr(wp, key, value)
        await self._session.flush()
        await self._session.refresh(wp)
        return wp
