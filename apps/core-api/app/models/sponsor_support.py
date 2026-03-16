"""SponsorSupport model."""

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SponsorSupport(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "sponsor_supports"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    sponsor_actor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("actors.id"), nullable=False
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("task_cards.id"), nullable=True
    )
    support_type: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")

    # Incremental fields
    support_goal: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_structure_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    support_effectiveness_score: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    consumed_units: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    source_event_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
