"""TaskCard model."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class TaskCard(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "task_cards"

    work_package_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("work_packages.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    input_conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_spec: Mapped[str] = mapped_column(Text, nullable=False)
    completion_criteria: Mapped[str] = mapped_column(Text, nullable=False)
    main_role: Mapped[str] = mapped_column(String(50), nullable=False)
    dependency_task_ids_json: Mapped[list | None] = mapped_column(JSONB, nullable=True)  # type: ignore[type-arg]
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False, default="low")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    ewu: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("1.00"))
    rwu: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    swu: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    has_reward: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Incremental fields
    raw_goal: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_output_spec: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_completion_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalized_goal: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalized_output_spec: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalized_completion_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    criticality_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    collaboration_complexity_score: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    feature_snapshot_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    last_feature_computed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    graph_exportable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    structural_role_hint: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Delivery evidence & verification fields
    verification_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="unverified"
    )
    completion_mode: Mapped[str] = mapped_column(
        String(50), nullable=False, default="evidence_backed"
    )
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
