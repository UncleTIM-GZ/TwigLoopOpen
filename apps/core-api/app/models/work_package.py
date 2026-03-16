"""WorkPackage model."""

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class WorkPackage(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "work_packages"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Incremental fields
    task_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_ewu: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    dependency_density: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    main_task_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    main_role_needed: Mapped[str | None] = mapped_column(String(50), nullable=True)
    feature_snapshot_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
