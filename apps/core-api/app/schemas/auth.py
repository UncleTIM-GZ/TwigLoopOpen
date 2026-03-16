"""Auth request/response schemas."""

import uuid
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=100)
    entry_intent: Literal["founder", "collaborator", "both"] = "both"

    model_config = {"extra": "forbid"}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    model_config = {"extra": "forbid"}


class RefreshTokenRequest(BaseModel):
    refresh_token: str

    model_config = {"extra": "forbid"}


class AuthResponse(BaseModel):
    account_id: uuid.UUID
    actor_id: uuid.UUID
    access_token: str
    refresh_token: str
