"""Domain event repository — data access for domain_events table."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain_event import DomainEvent


class DomainEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, event: DomainEvent) -> DomainEvent:
        self._session.add(event)
        await self._session.flush()
        return event

    async def find_by_aggregate(
        self,
        aggregate_type: str,
        aggregate_id: uuid.UUID,
        *,
        limit: int = 50,
    ) -> list[DomainEvent]:
        stmt = (
            select(DomainEvent)
            .where(
                DomainEvent.aggregate_type == aggregate_type,
                DomainEvent.aggregate_id == aggregate_id,
            )
            .order_by(DomainEvent.occurred_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
