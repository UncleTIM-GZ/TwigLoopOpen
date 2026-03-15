"""Source request/response schemas."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class BindRepoRequest(BaseModel):
    repo_url: str = Field(min_length=1, max_length=500)
    source_type: Literal["github", "gitee"] = "github"
    external_repo_id: str | None = None

    model_config = {"extra": "forbid"}


class SourceResponse(BaseModel):
    source_id: uuid.UUID
    project_id: uuid.UUID
    source_type: str
    repo_url: str
    binding_status: str
    external_repo_id: str | None = None
    created_at: datetime
    updated_at: datetime
