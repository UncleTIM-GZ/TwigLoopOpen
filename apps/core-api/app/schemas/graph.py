"""Graph response schemas — edges and feature snapshots."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

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
    source_event_id: uuid.UUID | None = None
    source_object_type: str | None = None
    source_object_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


class ActorActorEdgeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    actor_a_id: uuid.UUID
    actor_b_id: uuid.UUID
    edge_type: str
    project_id: uuid.UUID | None = None
    task_id: uuid.UUID | None = None
    weight: Decimal
    confidence: Decimal
    status: str
    valid_from: datetime
    valid_to: datetime | None = None
    source_event_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


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
    feature_json: dict[str, Any]
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
    feature_json: dict[str, Any]
    computed_at: datetime
