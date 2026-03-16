"""Actor repository — data access for actors table."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.actor import Actor


class ActorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_account_id(self, account_id: uuid.UUID) -> Actor | None:
        stmt = select(Actor).where(Actor.account_id == account_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id(self, actor_id: uuid.UUID) -> Actor | None:
        stmt = select(Actor).where(Actor.id == actor_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, actor: Actor) -> Actor:
        self._session.add(actor)
        await self._session.flush()
        return actor

    async def update_fields(self, actor: Actor, updates: dict[str, object]) -> Actor:
        """Apply a dict of field updates to an actor."""
        for key, value in updates.items():
            setattr(actor, key, value)
        await self._session.flush()
        await self._session.refresh(actor)
        return actor
