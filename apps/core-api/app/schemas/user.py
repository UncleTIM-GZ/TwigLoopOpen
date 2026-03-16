"""User profile schemas."""

import uuid

from pydantic import BaseModel, field_validator


class AccountInfo(BaseModel):
    account_id: uuid.UUID
    email: str


class ActorInfo(BaseModel):
    actor_id: uuid.UUID
    display_name: str
    actor_type: str
    bio: str | None = None
    availability: str | None = None
    skills: list[str] | None = None
    interested_project_types: list[str] | None = None
    is_founder: bool
    is_collaborator: bool
    is_reviewer: bool
    is_sponsor: bool
    profile_status: str
    level: str


class MeResponse(BaseModel):
    account: AccountInfo
    actor: ActorInfo


class UpdateProfileRequest(BaseModel):
    display_name: str | None = None
    bio: str | None = None
    availability: str | None = None
    skills: list[str] | None = None
    interested_project_types: list[str] | None = None

    model_config = {"extra": "forbid"}

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            if len(v) > 50:
                msg = "Maximum 50 skills allowed"
                raise ValueError(msg)
            for item in v:
                if len(item) > 100:
                    msg = "Each skill must be 100 characters or less"
                    raise ValueError(msg)
        return v

    @field_validator("interested_project_types")
    @classmethod
    def validate_project_types(cls, v: list[str] | None) -> list[str] | None:
        if v is not None and len(v) > 10:
            msg = "Maximum 10 project types allowed"
            raise ValueError(msg)
        return v
