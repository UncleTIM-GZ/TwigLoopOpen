"""Task card request/response schemas."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class CreateTaskCardRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    task_type: Literal[
        "requirement_clarification",
        "research",
        "product_design",
        "development",
        "testing_fix",
        "documentation",
        "collaboration_support",
        "review_audit",
    ]
    goal: str = Field(min_length=1)
    input_conditions: str | None = None
    output_spec: str = Field(min_length=1)
    completion_criteria: str = Field(min_length=1)
    main_role: str = Field(min_length=1, max_length=50)
    risk_level: Literal["low", "medium", "high"] = "low"
    ewu: Decimal = Field(default=Decimal("1.0"), ge=0)

    model_config = {"extra": "forbid"}


class UpdateTaskCardRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    goal: str | None = Field(default=None, min_length=1)
    output_spec: str | None = Field(default=None, min_length=1)
    completion_criteria: str | None = Field(default=None, min_length=1)
    ewu: Decimal | None = Field(default=None, ge=0)

    model_config = {"extra": "forbid"}


class TaskCardResponse(BaseModel):
    task_id: uuid.UUID
    work_package_id: uuid.UUID
    title: str
    task_type: str
    goal: str
    input_conditions: str | None = None
    output_spec: str
    completion_criteria: str
    main_role: str
    risk_level: str
    status: str
    ewu: Decimal
    rwu: Decimal | None = None
    swu: Decimal | None = None
    has_reward: bool
    created_at: datetime
    updated_at: datetime
