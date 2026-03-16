"""Draft request/response schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CreateDraftRequest(BaseModel):
    draft_type: str = Field(min_length=1, max_length=64)
    source_channel: str = Field(default="mcp", max_length=32)
    collected_fields_json: dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "forbid"}


class UpdateDraftRequest(BaseModel):
    collected_fields_json: dict[str, Any] | None = None
    missing_fields_json: list[Any] | None = None
    warnings_json: list[Any] | None = None
    last_llm_summary: str | None = None
    preflight_status: str | None = None
    preflight_result_json: dict[str, Any] | None = None

    model_config = {"extra": "forbid"}


class DraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    actor_id: uuid.UUID
    draft_type: str
    source_channel: str
    collected_fields_json: dict[str, Any]
    missing_fields_json: list[Any]
    warnings_json: list[Any]
    preflight_status: str
    preflight_result_json: dict[str, Any] | None = None
    last_llm_summary: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
