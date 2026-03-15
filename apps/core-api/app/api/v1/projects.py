"""Project routes — CRUD."""

import uuid

from fastapi import APIRouter, Depends, Query
from shared_auth import CurrentUser, get_current_user
from shared_schemas import ApiResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.project import (
    CreateProjectRequest,
    ProjectListParams,
    ProjectResponse,
    UpdateProjectRequest,
)
from app.schemas.status import StatusTransitionRequest
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", status_code=201)  # type: ignore[untyped-decorator]
async def create_project(
    body: CreateProjectRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ProjectResponse]:
    service = ProjectService(session)
    result = await service.create(body, user)
    return ApiResponse(success=True, data=result)


@router.get("/")  # type: ignore[untyped-decorator]
async def list_projects(
    project_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ProjectResponse]]:
    service = ProjectService(session)
    params = ProjectListParams(project_type=project_type, status=status, page=page, limit=limit)
    items, meta = await service.get_list(params)
    return ApiResponse(success=True, data=items, meta=meta.model_dump())


@router.get("/{project_id}")  # type: ignore[untyped-decorator]
async def get_project(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ProjectResponse]:
    service = ProjectService(session)
    result = await service.get_by_id(project_id)
    return ApiResponse(success=True, data=result)


@router.patch("/{project_id}")  # type: ignore[untyped-decorator]
async def update_project(
    project_id: uuid.UUID,
    body: UpdateProjectRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ProjectResponse]:
    service = ProjectService(session)
    result = await service.update(project_id, body, user)
    return ApiResponse(success=True, data=result)


@router.patch("/{project_id}/status")  # type: ignore[untyped-decorator]
async def transition_project_status(
    project_id: uuid.UUID,
    body: StatusTransitionRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ProjectResponse]:
    service = ProjectService(session)
    result = await service.transition_status(project_id, body.status, user)
    return ApiResponse(success=True, data=result)
