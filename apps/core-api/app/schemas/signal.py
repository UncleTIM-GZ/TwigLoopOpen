"""Signal request/response schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class SignalResponse(BaseModel):
    signal_id: uuid.UUID
    project_id: uuid.UUID
    signal_type: str
    source_type: str
    source_ref: str | None = None
    payload_json: dict[str, Any] | None = None
    occurred_at: datetime
