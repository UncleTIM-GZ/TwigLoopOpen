"""ReviewRecord model."""

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ReviewRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "review_records"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    reviewer_actor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("actors.id"), nullable=False
    )
    milestone: Mapped[str] = mapped_column(String(128), nullable=False)
    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Incremental fields
    review_scope: Mapped[str | None] = mapped_column(String(64), nullable=True)
    review_complexity_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    review_cycle_index: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    source_event_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
