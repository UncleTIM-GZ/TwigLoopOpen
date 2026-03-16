"""Quota rules and preflight check routes."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from shared_auth import CurrentUser, get_current_user
from shared_schemas import ApiResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.domain.quota_config import (
    ACTIVE_PROJECT_STATUSES,
    ACTIVE_TASK_STATUSES,
    MAX_ACTIVE_PROJECTS_NEW_FOUNDER,
    MAX_ACTIVE_TASKS_DEFAULT,
    MAX_EWU_PER_TASK,
    MAX_OPEN_SEATS_DEFAULT,
    MAX_PENDING_APPLICATIONS_PER_PROJECT,
    MAX_PENDING_APPLICATIONS_PER_TASK,
    MAX_TASKS_PER_PROJECT,
    MAX_TASKS_PER_WORK_PACKAGE,
    MAX_WORK_PACKAGES_PER_PROJECT,
    OPEN_SEAT_STATUSES,
    PENDING_APPLICATION_STATUSES,
)
from app.services.quota_preflight_service import QuotaPreflightService

router = APIRouter(prefix="/quotas", tags=["quotas"])


# ---- request schemas ----


class CheckProjectQuotaRequest(BaseModel):
    """Body for project quota preflight check."""

    work_packages: list[dict[str, Any]] = Field(default_factory=list)


class CheckApplicationQuotaRequest(BaseModel):
    """Body for application quota preflight check."""

    project_id: uuid.UUID
    task_id: uuid.UUID | None = None


# ---- endpoints ----


@router.get("/rules")  # type: ignore[untyped-decorator]
async def get_quota_rules() -> ApiResponse[dict[str, Any]]:
    """Get all platform quota rules and their current limits."""
    return ApiResponse(
        success=True,
        data={
            "object_limits": {
                "max_work_packages_per_project": MAX_WORK_PACKAGES_PER_PROJECT,
                "max_tasks_per_work_package": MAX_TASKS_PER_WORK_PACKAGE,
                "max_tasks_per_project": MAX_TASKS_PER_PROJECT,
                "max_ewu_per_task": MAX_EWU_PER_TASK,
            },
            "founder_limits": {
                "max_active_projects": MAX_ACTIVE_PROJECTS_NEW_FOUNDER,
                "max_open_seats": MAX_OPEN_SEATS_DEFAULT,
                "max_active_tasks": MAX_ACTIVE_TASKS_DEFAULT,
            },
            "relationship_limits": {
                "max_pending_applications_per_project": MAX_PENDING_APPLICATIONS_PER_PROJECT,
                "max_pending_applications_per_task": MAX_PENDING_APPLICATIONS_PER_TASK,
            },
            "status_definitions": {
                "active_project_statuses": list(ACTIVE_PROJECT_STATUSES),
                "open_seat_statuses": list(OPEN_SEAT_STATUSES),
                "active_task_statuses": list(ACTIVE_TASK_STATUSES),
                "pending_application_statuses": list(PENDING_APPLICATION_STATUSES),
            },
        },
    )


@router.post("/check-project")  # type: ignore[untyped-decorator]
async def check_project_quota(
    body: CheckProjectQuotaRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict[str, Any]]:
    """Run quota preflight on project data."""
    service = QuotaPreflightService(session)
    violations = await service.check_project_quota(
        draft_id_or_fields=body.model_dump(),
        actor_id=user.actor_id,
    )
    return ApiResponse(
        success=True,
        data={
            "passed": len([v for v in violations if v.severity == "error"]) == 0,
            "violations": [v.to_dict() for v in violations],
        },
    )


@router.post("/check-application")  # type: ignore[untyped-decorator]
async def check_application_quota(
    body: CheckApplicationQuotaRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[dict[str, Any]]:
    """Run quota preflight on application."""
    service = QuotaPreflightService(session)
    violations = await service.check_application_quota(
        project_id=body.project_id,
        task_id=body.task_id,
    )
    return ApiResponse(
        success=True,
        data={
            "passed": len([v for v in violations if v.severity == "error"]) == 0,
            "violations": [v.to_dict() for v in violations],
        },
    )
