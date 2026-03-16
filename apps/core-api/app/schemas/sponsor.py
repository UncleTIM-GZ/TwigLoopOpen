"""Sponsor support request/response schemas."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class CreateSupportRequest(BaseModel):
    project_id: uuid.UUID
    support_type: Literal["financial", "resource", "mentorship"]
    amount: Decimal | None = Field(default=None, ge=0)

    model_config = {"extra": "forbid"}


class SupportResponse(BaseModel):
    support_id: uuid.UUID
    project_id: uuid.UUID
    sponsor_actor_id: uuid.UUID
    support_type: str
    amount: Decimal | None = None
    status: str
    created_at: datetime
