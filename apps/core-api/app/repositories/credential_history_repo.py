"""CredentialHistory repository — data access for credential audit trail."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.credential_history import CredentialHistory


class CredentialHistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, entry: CredentialHistory) -> CredentialHistory:
        self._session.add(entry)
        await self._session.flush()
        return entry

    async def find_by_credential(self, credential_id: uuid.UUID) -> list[CredentialHistory]:
        stmt = (
            select(CredentialHistory)
            .where(CredentialHistory.credential_id == credential_id)
            .order_by(CredentialHistory.occurred_at.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
