"""State transition request/response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StateTransitionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    object_type: str
    object_id: uuid.UUID
    from_status: str | None = None
    to_status: str
    trigger_actor_id: uuid.UUID | None = None
    trigger_reason: str | None = None
    occurred_at: datetime
