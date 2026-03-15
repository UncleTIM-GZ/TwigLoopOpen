"""State transition repository — data access for state_transition_events table."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.state_transition import StateTransitionEvent


class StateTransitionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, event: StateTransitionEvent) -> StateTransitionEvent:
        self._session.add(event)
        await self._session.flush()
        return event

    async def find_by_object(
        self,
        object_type: str,
        object_id: uuid.UUID,
        *,
        limit: int = 50,
    ) -> list[StateTransitionEvent]:
        stmt = (
            select(StateTransitionEvent)
            .where(
                StateTransitionEvent.object_type == object_type,
                StateTransitionEvent.object_id == object_id,
            )
            .order_by(StateTransitionEvent.occurred_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
