"""VerifiableCredential repository — data access for verifiable_credentials table."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.verifiable_credential import VerifiableCredential


class VerifiableCredentialRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, vc_id: uuid.UUID) -> VerifiableCredential | None:
        stmt = select(VerifiableCredential).where(VerifiableCredential.id == vc_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_actor(self, actor_id: uuid.UUID) -> list[VerifiableCredential]:
        stmt = (
            select(VerifiableCredential)
            .where(VerifiableCredential.actor_id == actor_id)
            .order_by(VerifiableCredential.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_paginated_by_actor(
        self, actor_id: uuid.UUID, *, offset: int = 0, limit: int = 20
    ) -> tuple[list[VerifiableCredential], int]:
        """Return (items, total_count) for credentials of an actor."""
        base_filter = VerifiableCredential.actor_id == actor_id

        count_stmt = select(func.count()).select_from(VerifiableCredential).where(base_filter)
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = (
            select(VerifiableCredential)
            .where(base_filter)
            .order_by(VerifiableCredential.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())
        return items, total

    async def create(self, vc: VerifiableCredential) -> VerifiableCredential:
        self._session.add(vc)
        await self._session.flush()
        return vc

    async def update_status(self, vc: VerifiableCredential, status: str) -> VerifiableCredential:
        vc.status = status
        await self._session.flush()
        await self._session.refresh(vc)
        return vc

    async def update_fields(
        self, vc: VerifiableCredential, updates: dict[str, object]
    ) -> VerifiableCredential:
        for key, value in updates.items():
            setattr(vc, key, value)
        await self._session.flush()
        await self._session.refresh(vc)
        return vc
