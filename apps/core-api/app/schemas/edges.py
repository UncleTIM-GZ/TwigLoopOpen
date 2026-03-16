"""Edge request/response schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ActorProjectEdgeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    actor_id: uuid.UUID
    project_id: uuid.UUID
    edge_type: str
    weight: Decimal
    confidence: Decimal
    status: str
    valid_from: datetime
    valid_to: datetime | None = None
    created_at: datetime


class ActorActorEdgeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    actor_a_id: uuid.UUID
    actor_b_id: uuid.UUID
    edge_type: str
    project_id: uuid.UUID | None = None
    weight: Decimal
    confidence: Decimal
    status: str
    created_at: datetime
