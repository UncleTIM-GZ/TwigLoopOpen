"""Signal repository — data access for project_signals table."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.signal import ProjectSignal


class SignalRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, signal_id: uuid.UUID) -> ProjectSignal | None:
        stmt = select(ProjectSignal).where(ProjectSignal.id == signal_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_project(
        self, project_id: uuid.UUID, *, limit: int = 50
    ) -> list[ProjectSignal]:
        stmt = (
            select(ProjectSignal)
            .where(ProjectSignal.project_id == project_id)
            .order_by(ProjectSignal.occurred_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, signal: ProjectSignal) -> ProjectSignal:
        self._session.add(signal)
        await self._session.flush()
        return signal
