"""Workflow trigger endpoints — start Temporal workflows from core-api."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, StringConstraints
from shared_auth import CurrentUser, get_current_user
from shared_auth.jwt import create_access_token
from shared_schemas import ApiResponse

router = APIRouter(prefix="/workflows", tags=["workflows"])


class PublishProjectWorkflowRequest(BaseModel):
    project_type: str
    founder_type: str
    title: str
    summary: str
    target_users: str | None = None
    work_packages: list[dict[str, Any]] = Field(default_factory=list)


class StartWorkflowResponse(BaseModel):
    workflow_id: str


_UUID_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
UUIDStr = Annotated[str, StringConstraints(pattern=_UUID_PATTERN)]


class StartApplicationReviewRequest(BaseModel):
    project_id: UUIDStr
    motivation: str
    preferred_role: str = "collaborator"


class StartPublicBenefitReviewRequest(BaseModel):
    project_id: UUIDStr
    milestone: str
    reviewer_id: UUIDStr


@router.post("/publish-project")
async def start_publish_project_workflow(
    req: PublishProjectWorkflowRequest,
    user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[dict[str, Any]]:
    """Start a project publish workflow via Temporal."""
    try:
        from temporal.starter import start_publish_project

        token = create_access_token(user.account_id, user.actor_id, user.roles)
        result = await start_publish_project(
            token=token,
            project_type=req.project_type,
            founder_type=req.founder_type,
            title=req.title,
            summary=req.summary,
            work_packages=req.work_packages,
            target_users=req.target_users,
        )
    except Exception as err:
        raise HTTPException(status_code=502, detail=f"Workflow service unavailable: {err}") from err
    return ApiResponse(
        success=True,
        data={
            "project_id": result.project_id,
            "work_package_ids": result.work_package_ids,
            "task_ids": result.task_ids,
        },
    )


@router.post("/application-review")
async def start_application_review_workflow(
    req: StartApplicationReviewRequest,
    user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[StartWorkflowResponse]:
    """Start an application review workflow via Temporal."""
    try:
        from temporal.starter import start_application_review

        token = create_access_token(user.account_id, user.actor_id, user.roles)
        wf_id = await start_application_review(
            token=token,
            project_id=req.project_id,
            applicant_actor_id=str(user.actor_id),
            motivation=req.motivation,
            preferred_role=req.preferred_role,
        )
    except Exception as err:
        raise HTTPException(status_code=502, detail=f"Workflow service unavailable: {err}") from err
    return ApiResponse(success=True, data=StartWorkflowResponse(workflow_id=wf_id))


@router.post("/public-benefit-review")
async def start_public_benefit_review_workflow(
    req: StartPublicBenefitReviewRequest,
    user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[StartWorkflowResponse]:
    """Start a public benefit review workflow via Temporal."""
    try:
        from temporal.starter import start_public_benefit_review

        token = create_access_token(user.account_id, user.actor_id, user.roles)
        wf_id = await start_public_benefit_review(
            token=token,
            project_id=req.project_id,
            milestone=req.milestone,
            reviewer_id=req.reviewer_id,
        )
    except Exception as err:
        raise HTTPException(status_code=502, detail=f"Workflow service unavailable: {err}") from err
    return ApiResponse(success=True, data=StartWorkflowResponse(workflow_id=wf_id))
