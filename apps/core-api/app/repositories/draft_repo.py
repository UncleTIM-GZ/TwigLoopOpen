"""Draft repository — data access for drafts table."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.draft import Draft


class DraftRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, draft: Draft) -> Draft:
        self._session.add(draft)
        await self._session.flush()
        return draft

    async def find_by_id(self, draft_id: uuid.UUID) -> Draft | None:
        stmt = select(Draft).where(Draft.id == draft_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_actor(self, actor_id: uuid.UUID) -> list[Draft]:
        stmt = select(Draft).where(Draft.actor_id == actor_id).order_by(Draft.updated_at.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_fields(self, draft: Draft, updates: dict[str, object]) -> Draft:
        for key, value in updates.items():
            setattr(draft, key, value)
        await self._session.flush()
        await self._session.refresh(draft)
        return draft

    async def delete(self, draft: Draft) -> None:
        await self._session.delete(draft)
        await self._session.flush()
