"""Status transition and EWU schemas."""

from decimal import Decimal

from pydantic import BaseModel, Field


class StatusTransitionRequest(BaseModel):
    status: str = Field(min_length=1)

    model_config = {"extra": "forbid"}


class EwuCalculateRequest(BaseModel):
    task_type: str
    risk_level: str
    complexity: int = Field(ge=1, le=5)
    criticality: int = Field(ge=1, le=5)
    collaboration_complexity: int = Field(ge=1, le=5)

    model_config = {"extra": "forbid"}


class EwuCalculateResponse(BaseModel):
    ewu: Decimal
    breakdown: str
