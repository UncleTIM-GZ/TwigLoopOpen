"""Application and seat request/response schemas."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CreateApplicationRequest(BaseModel):
    seat_preference: Literal["growth", "formal"]
    intended_role: str = Field(min_length=1, max_length=100)
    motivation: str | None = None
    availability: str | None = None

    model_config = {"extra": "forbid"}


class ReviewApplicationRequest(BaseModel):
    decision: Literal["accepted", "rejected", "converted_to_growth_seat"]

    model_config = {"extra": "forbid"}


class ApplicationResponse(BaseModel):
    application_id: uuid.UUID
    project_id: uuid.UUID
    actor_id: uuid.UUID
    seat_preference: str
    intended_role: str
    motivation: str | None = None
    availability: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    reviewed_at: datetime | None = None


class SeatResponse(BaseModel):
    seat_id: uuid.UUID
    project_id: uuid.UUID
    actor_id: uuid.UUID | None = None
    seat_type: str
    role_needed: str
    status: str
    reward_enabled: bool
    created_at: datetime
    updated_at: datetime
