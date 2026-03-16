"""Domain event request/response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DomainEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    event_type: str
    aggregate_type: str
    aggregate_id: uuid.UUID
    actor_id: uuid.UUID | None = None
    payload_json: dict[str, object] | None = None
    occurred_at: datetime
    source_channel: str


class DomainEventListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    event_type: str
    aggregate_type: str
    aggregate_id: uuid.UUID
    occurred_at: datetime
