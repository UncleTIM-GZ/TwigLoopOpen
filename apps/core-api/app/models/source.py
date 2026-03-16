"""ProjectSource model."""

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ProjectSource(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_sources"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    repo_url: Mapped[str] = mapped_column(String(500), nullable=False)
    binding_status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    external_repo_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
