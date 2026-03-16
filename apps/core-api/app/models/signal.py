"""ProjectSignal model."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class ProjectSignal(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "project_signals"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    signal_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # type: ignore[type-arg]
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Incremental fields
    normalized_signal_weight: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    signal_group: Mapped[str | None] = mapped_column(String(64), nullable=True)
    derived_from_event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    is_structural_signal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
