"""Feature snapshot request/response schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ActorFeatureSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    actor_id: uuid.UUID
    version: int
    dominant_project_type: str | None = None
    dominant_task_type: str | None = None
    completion_rate: Decimal | None = None
    reuse_count: int
    collaboration_breadth: int
    coordination_load_score: Decimal | None = None
    public_benefit_participation_score: Decimal | None = None
    review_reliability_score: Decimal | None = None
    feature_json: dict[str, object] | None = None
    computed_at: datetime


class ProjectFeatureSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    version: int
    task_count: int
    avg_ewu: Decimal | None = None
    max_ewu: Decimal | None = None
    dependency_density: Decimal | None = None
    role_diversity_score: Decimal | None = None
    start_pattern: str | None = None
    project_complexity_score: Decimal | None = None
    feature_json: dict[str, object] | None = None
    computed_at: datetime
