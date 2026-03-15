"""ProjectApplication model."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ProjectApplication(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_applications"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    actor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("actors.id"), nullable=False
    )
    seat_preference: Mapped[str] = mapped_column(String(50), nullable=False)
    intended_role: Mapped[str] = mapped_column(String(100), nullable=False)
    motivation: Mapped[str | None] = mapped_column(Text, nullable=True)
    availability: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="submitted")
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Incremental fields
    application_source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    match_score_rule: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    match_score_signal: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    match_score_structural: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    final_match_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    decision_reason_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
