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


class VerifyResponse(BaseModel):
    """Minimal public verification response — no internal IDs or data."""

    valid: bool
    credential_type: str | None = None
    issued_at: datetime | None = None
