"""Project model."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Project(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    founder_actor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("actors.id"), nullable=False
    )
    project_type: Mapped[str] = mapped_column(String(50), nullable=False)
    founder_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    target_users: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_stage: Mapped[str] = mapped_column(String(50), nullable=False, default="idea")
    min_start_step: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    needs_human_reviewer: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    human_review_status: Mapped[str] = mapped_column(String(50), nullable=False, default="none")
    has_reward: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_sponsor: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_via: Mapped[str] = mapped_column(String(50), nullable=False, default="web")

    # Incremental fields
    feature_snapshot_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    last_feature_computed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    task_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_ewu: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    max_ewu: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    dependency_density: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    role_diversity_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    start_pattern: Mapped[str | None] = mapped_column(String(128), nullable=True)
    project_complexity_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    structural_cluster_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
