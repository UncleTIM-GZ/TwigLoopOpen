"""AgentBrief model — persisted matching/review briefs from agent delegations.

A single table stores both MatchingBrief and ReviewBrief via brief_type field.
Content is stored as JSONB for flexibility across brief types.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class AgentBrief(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "agent_briefs"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("task_cards.id"), nullable=False, index=True
    )
    brief_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # matching_brief | review_brief
    brief_source: Mapped[str] = mapped_column(
        String(50), nullable=False, default="rule_based"
    )  # rule_based | llm
    brief_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )  # active | superseded

    content_json: Mapped[dict] = mapped_column(JSONB, nullable=False)  # type: ignore[type-arg]

    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    delegation_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
