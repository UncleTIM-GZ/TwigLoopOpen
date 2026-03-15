"""Work package request/response schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CreateWorkPackageRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    sort_order: int = 0

    model_config = {"extra": "forbid"}


class UpdateWorkPackageRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    sort_order: int | None = None

    model_config = {"extra": "forbid"}


class WorkPackageResponse(BaseModel):
    work_package_id: uuid.UUID
    project_id: uuid.UUID
    title: str
    description: str | None = None
    status: str
    sort_order: int
    created_at: datetime
    updated_at: datetime

    # Aggregated from child task cards (computed, not stored)
    total_ewu: Decimal = Decimal("0")
    avg_ewu: Decimal | None = None
    total_rwu: Decimal | None = None
    total_swu: Decimal | None = None
    task_count: int = 0
