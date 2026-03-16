"""Seat repository."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.seat import ProjectSeat


class SeatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_project(self, project_id: uuid.UUID) -> list[ProjectSeat]:
        stmt = (
            select(ProjectSeat)
            .where(ProjectSeat.project_id == project_id)
            .order_by(ProjectSeat.created_at)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_paginated_by_project(
        self, project_id: uuid.UUID, *, offset: int = 0, limit: int = 20
    ) -> tuple[list[ProjectSeat], int]:
        """Return (items, total_count) for seats in a project."""
        base_filter = ProjectSeat.project_id == project_id

        count_stmt = select(func.count()).select_from(ProjectSeat).where(base_filter)
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = (
            select(ProjectSeat)
            .where(base_filter)
            .order_by(ProjectSeat.created_at)
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())
        return items, total

    async def create(self, seat: ProjectSeat) -> ProjectSeat:
        self._session.add(seat)
        await self._session.flush()
        return seat
