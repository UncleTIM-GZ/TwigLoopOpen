"""Snapshot repositories — data access for feature snapshot tables."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.snapshots import ActorFeatureSnapshot, ProjectFeatureSnapshot


class ActorFeatureSnapshotRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, snapshot: ActorFeatureSnapshot) -> ActorFeatureSnapshot:
        self._session.add(snapshot)
        await self._session.flush()
        return snapshot

    async def find_latest(self, actor_id: uuid.UUID) -> ActorFeatureSnapshot | None:
        stmt = (
            select(ActorFeatureSnapshot)
            .where(ActorFeatureSnapshot.actor_id == actor_id)
            .order_by(ActorFeatureSnapshot.computed_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()


class ProjectFeatureSnapshotRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, snapshot: ProjectFeatureSnapshot) -> ProjectFeatureSnapshot:
        self._session.add(snapshot)
        await self._session.flush()
        return snapshot

    async def find_latest(self, project_id: uuid.UUID) -> ProjectFeatureSnapshot | None:
        stmt = (
            select(ProjectFeatureSnapshot)
            .where(ProjectFeatureSnapshot.project_id == project_id)
            .order_by(ProjectFeatureSnapshot.computed_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
