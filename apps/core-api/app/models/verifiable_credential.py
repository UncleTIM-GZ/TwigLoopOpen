"""VerifiableCredential model.

Status lifecycle:
  draft → issued → [suspended | revoked | superseded]
  suspended → [issued (reactivated) | revoked]
  issued/suspended → expired (when valid_until passes)
  revoked, superseded, expired → terminal (no further transitions)
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class VerifiableCredential(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "verifiable_credentials"

    actor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("actors.id"), nullable=False
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("task_cards.id"), nullable=True
    )
    credential_type: Mapped[str] = mapped_column(String(100), nullable=False)
    credential_data_json: Mapped[dict] = mapped_column(JSONB, nullable=False)  # type: ignore[type-arg]
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Incremental fields
    credential_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    credential_source_event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    credential_source_relation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    feature_snapshot_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Evidence-backed issuance fields
    evidence_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("delivery_evidences.id"), nullable=True
    )
    verification_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("task_verifications.id"), nullable=True
    )
    issuance_basis: Mapped[str] = mapped_column(String(50), nullable=False, default="verified")

    # Lifecycle fields — revoke, supersede, suspend, expire
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revocation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    revoked_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("actors.id"), nullable=True
    )
    superseded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("verifiable_credentials.id"), nullable=True
    )
    supersedes: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("verifiable_credentials.id"), nullable=True
    )

    # H3.2: suspended + expiry
    suspended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    suspension_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    suspended_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("actors.id"), nullable=True
    )
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
