"""Event response schemas — domain events and state transitions."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class DomainEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    event_type: str
    aggregate_type: str
    aggregate_id: uuid.UUID
    actor_id: uuid.UUID | None = None
    payload_json: dict[str, Any]
    occurred_at: datetime
    correlation_id: uuid.UUID | None = None
    causation_id: uuid.UUID | None = None
    source_channel: str
    schema_version: int


class StateTransitionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    object_type: str
    object_id: uuid.UUID
    from_status: str | None = None
    to_status: str
    trigger_actor_id: uuid.UUID | None = None
    trigger_reason: str | None = None
    source_event_id: uuid.UUID | None = None
    occurred_at: datetime
