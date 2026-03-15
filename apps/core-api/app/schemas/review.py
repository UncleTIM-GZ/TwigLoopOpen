"""Review request/response schemas."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SubmitReviewRequest(BaseModel):
    decision: Literal["passed", "needs_revision", "rejected"]
    feedback: str | None = Field(default=None, max_length=2000)

    model_config = {"extra": "forbid"}


class ReviewResponse(BaseModel):
    project_id: uuid.UUID
    reviewer_actor_id: uuid.UUID
    decision: str
    feedback: str | None = None
    created_at: datetime
