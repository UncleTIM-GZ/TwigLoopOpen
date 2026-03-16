"""Evidence and verification request/response schemas."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SubmitEvidenceRequest(BaseModel):
    evidence_type: Literal["code_pr", "document", "design_file", "demo_url", "report", "other"]
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    evidence_url: str = Field(min_length=1, max_length=500)
    evidence_source: Literal["github", "figma", "google_docs", "notion", "manual"] = "manual"

    model_config = {"extra": "forbid"}


class EvidenceResponse(BaseModel):
    evidence_id: uuid.UUID
    task_id: uuid.UUID
    actor_id: uuid.UUID
    evidence_type: str
    title: str
    description: str | None = None
    evidence_url: str
    evidence_source: str
    version: int
    is_latest: bool
    status: str
    reviewer_note: str | None = None
    created_at: datetime


class VerifyTaskRequest(BaseModel):
    decision: Literal["approved", "rejected", "needs_revision"]
    note: str | None = None

    model_config = {"extra": "forbid"}


class VerificationResponse(BaseModel):
    verification_id: uuid.UUID
    task_id: uuid.UUID
    evidence_id: uuid.UUID | None
    reviewer_id: uuid.UUID
    decision: str
    note: str | None = None
    created_at: datetime
