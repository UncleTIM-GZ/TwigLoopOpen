"""Project request/response schemas."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class CreateProjectRequest(BaseModel):
    project_type: Literal["general", "public_benefit", "recruitment"]
    founder_type: Literal["ordinary", "help_seeker", "contributor"]
    title: str = Field(min_length=1, max_length=255)
    summary: str = Field(min_length=1)
    target_users: str | None = None
    current_stage: str = "idea"
    min_start_step: str | None = None
    created_via: Literal["web", "mcp"] = "web"

    model_config = {"extra": "forbid"}


class UpdateProjectRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    summary: str | None = Field(default=None, min_length=1)
    target_users: str | None = None
    current_stage: str | None = None
    min_start_step: str | None = None

    model_config = {"extra": "forbid"}


class ProjectResponse(BaseModel):
    project_id: uuid.UUID
    founder_actor_id: uuid.UUID
    project_type: str
    founder_type: str
    title: str
    summary: str
    target_users: str | None = None
    current_stage: str
    min_start_step: str | None = None
    status: str
    needs_human_reviewer: bool
    human_review_status: str
    has_reward: bool
    has_sponsor: bool
    created_via: str
    created_at: datetime
    updated_at: datetime

    # Aggregated from all task cards across work packages (computed, not stored)
    total_ewu: Decimal = Decimal("0")
    avg_ewu: Decimal | None = None
    max_ewu: Decimal | None = None
    total_rwu: Decimal | None = None
    total_swu: Decimal | None = None
    task_count: int = 0


class ProjectListParams(BaseModel):
    project_type: str | None = None
    status: str | None = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
