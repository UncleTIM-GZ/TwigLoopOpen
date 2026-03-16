"""Actor model — business identity."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Actor(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "actors"

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    actor_type: Mapped[str] = mapped_column(String(50), nullable=False, default="human")
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    availability: Mapped[str | None] = mapped_column(String(100), nullable=True)
    skills_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # type: ignore[type-arg]
    interested_project_types_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # type: ignore[type-arg]
    is_founder: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_collaborator: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_reviewer: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_sponsor: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    profile_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="profile_incomplete"
    )
    level: Mapped[str] = mapped_column(String(10), nullable=False, default="L0")

    # Incremental fields
    feature_snapshot_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    last_feature_computed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    dominant_project_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    dominant_task_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reuse_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    collaboration_breadth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    coordination_load_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    structural_role_label: Mapped[str | None] = mapped_column(String(64), nullable=True)

    account: Mapped["Account"] = relationship(back_populates="actors")  # type: ignore[name-defined]  # noqa: F821
