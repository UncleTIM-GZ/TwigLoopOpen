"""Draft model."""

import uuid
from typing import Any

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Draft(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "drafts"

    actor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("actors.id"), nullable=False
    )
    draft_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_channel: Mapped[str] = mapped_column(String(32), nullable=False, server_default="mcp")
    collected_fields_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    missing_fields_json: Mapped[list[Any]] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    warnings_json: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, server_default="[]")
    preflight_status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="pending"
    )
    preflight_result_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    last_llm_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="collecting")
