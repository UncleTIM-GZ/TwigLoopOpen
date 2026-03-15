"""Event write service — writes domain events and state transitions."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain_event import DomainEvent
from app.models.state_transition import StateTransitionEvent
from app.repositories.domain_event_repo import DomainEventRepository
from app.repositories.state_transition_repo import StateTransitionRepository


class EventWriteService:
    """Writes domain events and state transitions. Shares session with caller."""

    def __init__(self, session: AsyncSession) -> None:
        self._event_repo = DomainEventRepository(session)
        self._transition_repo = StateTransitionRepository(session)

    async def record_domain_event(
        self,
        event_type: str,
        aggregate_type: str,
        aggregate_id: uuid.UUID,
        *,
        actor_id: uuid.UUID | None = None,
        payload: dict[str, object] | None = None,
        source_channel: str = "system",
        correlation_id: uuid.UUID | None = None,
    ) -> DomainEvent:
        event = DomainEvent(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            actor_id=actor_id,
            payload_json=payload or {},
            source_channel=source_channel,
            correlation_id=correlation_id,
        )
        return await self._event_repo.create(event)

    async def record_state_transition(
        self,
        object_type: str,
        object_id: uuid.UUID,
        from_status: str | None,
        to_status: str,
        *,
        trigger_actor_id: uuid.UUID | None = None,
        trigger_reason: str | None = None,
        source_event_id: uuid.UUID | None = None,
    ) -> StateTransitionEvent:
        transition = StateTransitionEvent(
            object_type=object_type,
            object_id=object_id,
            from_status=from_status,
            to_status=to_status,
            trigger_actor_id=trigger_actor_id,
            trigger_reason=trigger_reason,
            source_event_id=source_event_id,
        )
        return await self._transition_repo.create(transition)
