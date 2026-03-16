"""ProjectSeat model."""

import uuid
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ProjectSeat(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_seats"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("actors.id"), nullable=True
    )
    seat_type: Mapped[str] = mapped_column(String(50), nullable=False)
    role_needed: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="proposed")
    reward_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Incremental fields
    seat_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seat_goal: Mapped[str | None] = mapped_column(Text, nullable=True)
    seat_dependency_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    structural_importance_score: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    entered_via_application_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
