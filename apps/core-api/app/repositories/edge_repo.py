"""Edge repositories — data access for relation edge tables."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.edges import ActorActorEdge, ActorProjectEdge


class ActorProjectEdgeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, edge: ActorProjectEdge) -> ActorProjectEdge:
        self._session.add(edge)
        await self._session.flush()
        return edge

    async def find_by_actor(self, actor_id: uuid.UUID) -> list[ActorProjectEdge]:
        stmt = (
            select(ActorProjectEdge)
            .where(ActorProjectEdge.actor_id == actor_id)
            .order_by(ActorProjectEdge.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_project(self, project_id: uuid.UUID) -> list[ActorProjectEdge]:
        stmt = (
            select(ActorProjectEdge)
            .where(ActorProjectEdge.project_id == project_id)
            .order_by(ActorProjectEdge.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


class ActorActorEdgeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, edge: ActorActorEdge) -> ActorActorEdge:
        self._session.add(edge)
        await self._session.flush()
        return edge

    async def find_by_actor(self, actor_id: uuid.UUID) -> list[ActorActorEdge]:
        stmt = (
            select(ActorActorEdge)
            .where(
                (ActorActorEdge.actor_a_id == actor_id) | (ActorActorEdge.actor_b_id == actor_id)
            )
            .order_by(ActorActorEdge.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
