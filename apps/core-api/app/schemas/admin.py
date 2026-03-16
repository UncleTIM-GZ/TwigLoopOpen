"""Admin response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class AdminUserResponse(BaseModel):
    account_id: uuid.UUID
    email: str
    account_status: str
    actor_id: uuid.UUID | None = None
    display_name: str | None = None
    created_at: datetime


class AdminProjectResponse(BaseModel):
    project_id: uuid.UUID
    title: str
    project_type: str
    status: str
    founder_actor_id: uuid.UUID
    created_at: datetime


class AdminApplicationResponse(BaseModel):
    application_id: uuid.UUID
    project_id: uuid.UUID
    actor_id: uuid.UUID
    status: str
    intended_role: str
    created_at: datetime
