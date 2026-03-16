"""Work package routes."""

import uuid

from fastapi import APIRouter, Depends, Query
from shared_auth import CurrentUser, get_current_user
from shared_schemas import ApiResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.work_package import (
    CreateWorkPackageRequest,
    UpdateWorkPackageRequest,
    WorkPackageResponse,
)
from app.services.work_package_service import WorkPackageService

router = APIRouter(tags=["work-packages"])


@router.post(  # type: ignore[untyped-decorator]
    "/projects/{project_id}/work-packages", status_code=201
)
async def create_work_package(
    project_id: uuid.UUID,
    body: CreateWorkPackageRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[WorkPackageResponse]:
    service = WorkPackageService(session)
    result = await service.create(project_id, body, user)
    return ApiResponse(success=True, data=result)


@router.get("/projects/{project_id}/work-packages")  # type: ignore[untyped-decorator]
async def list_work_packages(
    project_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[WorkPackageResponse]]:
    service = WorkPackageService(session)
    items, meta = await service.get_list(project_id, page=page, limit=limit)
    return ApiResponse(success=True, data=items, meta=meta.model_dump())


@router.patch("/work-packages/{wp_id}")  # type: ignore[untyped-decorator]
async def update_work_package(
    wp_id: uuid.UUID,
    body: UpdateWorkPackageRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[WorkPackageResponse]:
    service = WorkPackageService(session)
    result = await service.update(wp_id, body, user)
    return ApiResponse(success=True, data=result)
