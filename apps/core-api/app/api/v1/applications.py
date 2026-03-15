"""Application and seat routes."""

import uuid

from fastapi import APIRouter, Depends, Query
from shared_auth import CurrentUser, get_current_user
from shared_schemas import ApiResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.application import (
    ApplicationResponse,
    CreateApplicationRequest,
    ReviewApplicationRequest,
    SeatResponse,
)
from app.services.application_service import ApplicationService

router = APIRouter(tags=["applications"])


@router.post(  # type: ignore[untyped-decorator]
    "/projects/{project_id}/applications", status_code=201
)
async def apply_to_project(
    project_id: uuid.UUID,
    body: CreateApplicationRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ApplicationResponse]:
    service = ApplicationService(session)
    result = await service.apply(project_id, body, user)
    return ApiResponse(success=True, data=result)


@router.get("/projects/{project_id}/applications")  # type: ignore[untyped-decorator]
async def list_applications(
    project_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ApplicationResponse]]:
    service = ApplicationService(session)
    items, meta = await service.get_list_by_project(project_id, user, page=page, limit=limit)
    return ApiResponse(success=True, data=items, meta=meta.model_dump())


@router.patch("/applications/{app_id}")  # type: ignore[untyped-decorator]
async def review_application(
    app_id: uuid.UUID,
    body: ReviewApplicationRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ApplicationResponse]:
    service = ApplicationService(session)
    result = await service.review(app_id, body, user)
    return ApiResponse(success=True, data=result)


@router.patch("/applications/{app_id}/withdraw")  # type: ignore[untyped-decorator]
async def withdraw_application(
    app_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ApplicationResponse]:
    service = ApplicationService(session)
    result = await service.withdraw(app_id, user)
    return ApiResponse(success=True, data=result)


@router.get("/projects/{project_id}/seats")  # type: ignore[untyped-decorator]
async def list_seats(
    project_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[SeatResponse]]:
    service = ApplicationService(session)
    items, meta = await service.get_list_seats(project_id, user, page=page, limit=limit)
    return ApiResponse(success=True, data=items, meta=meta.model_dump())
