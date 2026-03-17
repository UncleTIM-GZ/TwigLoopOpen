"""Verifiable Credential schemas."""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


class IssueCredentialRequest(BaseModel):
    actor_id: uuid.UUID
    credential_type: Literal["task_completion", "project_participation"]
    project_id: uuid.UUID | None = None
    task_id: uuid.UUID | None = None

    model_config = {"extra": "forbid"}


class CredentialResponse(BaseModel):
    credential_id: uuid.UUID
    actor_id: uuid.UUID
    project_id: uuid.UUID | None = None
    task_id: uuid.UUID | None = None
    credential_type: str
    credential_data: dict[str, Any]
    status: str
    issued_at: datetime | None = None
    created_at: datetime


class RevokeCredentialRequest(BaseModel):
    reason: str

    model_config = {"extra": "forbid"}


class SuspendCredentialRequest(BaseModel):
    reason: str

    model_config = {"extra": "forbid"}


class CredentialStatusResponse(BaseModel):
    """Credential lifecycle status (public-safe — no internal reasons)."""

    credential_id: uuid.UUID
    status: str
    issued_at: datetime | None = None
    valid_until: datetime | None = None
    revoked_at: datetime | None = None
    suspended_at: datetime | None = None
    superseded_by: uuid.UUID | None = None
    supersedes: uuid.UUID | None = None
    credential_version: int = 1


class CredentialHistoryEntry(BaseModel):
    """Single credential lifecycle event (internal view)."""

    history_id: uuid.UUID
    credential_id: uuid.UUID
    event_type: str
    previous_status: str | None = None
    new_status: str
    source: str = "platform"
    occurred_at: datetime


class CredentialHistoryPublicEntry(BaseModel):
    """Single credential lifecycle event (public-safe)."""

    event_type: str
    new_status: str
    occurred_at: datetime


class VerifyResponse(BaseModel):
    """Minimal public verification response — no internal IDs or data."""

    valid: bool
    credential_type: str | None = None
    issued_at: datetime | None = None
