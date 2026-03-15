"""Feature snapshot models for actors and projects."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class ActorFeatureSnapshot(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "actor_feature_snapshots"

    actor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("actors.id"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    dominant_project_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    dominant_task_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    completion_rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    reuse_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    collaboration_breadth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    coordination_load_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    public_benefit_participation_score: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    review_reliability_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    feature_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")  # type: ignore[type-arg]
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ProjectFeatureSnapshot(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "project_feature_snapshots"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    task_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_ewu: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    max_ewu: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    dependency_density: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    role_diversity_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    start_pattern: Mapped[str | None] = mapped_column(String(128), nullable=True)
    project_complexity_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    feature_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")  # type: ignore[type-arg]
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
