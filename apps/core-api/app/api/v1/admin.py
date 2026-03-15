"""Admin routes — read-only listing + freeze/hide."""

import uuid

from fastapi import APIRouter, Depends, Query
from shared_auth import CurrentUser, require_role
from shared_schemas import ApiResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.admin import AdminApplicationResponse, AdminProjectResponse, AdminUserResponse
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])

_admin_dep = require_role("admin")


@router.get("/users")  # type: ignore[untyped-decorator]
async def list_users(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    _user: CurrentUser = Depends(_admin_dep),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[AdminUserResponse]]:
    service = AdminService(session)
    items, meta = await service.list_users(page, limit)
    return ApiResponse(success=True, data=items, meta=meta.model_dump())


@router.get("/projects")  # type: ignore[untyped-decorator]
async def list_projects(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    _user: CurrentUser = Depends(_admin_dep),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[AdminProjectResponse]]:
    service = AdminService(session)
    items, meta = await service.list_projects(page, limit)
    return ApiResponse(success=True, data=items, meta=meta.model_dump())


@router.get("/applications")  # type: ignore[untyped-decorator]
async def list_applications(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    _user: CurrentUser = Depends(_admin_dep),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[AdminApplicationResponse]]:
    service = AdminService(session)
    items, meta = await service.list_applications(page, limit)
    return ApiResponse(success=True, data=items, meta=meta.model_dump())


@router.patch("/users/{actor_id}/freeze")  # type: ignore[untyped-decorator]
async def freeze_user(
    actor_id: uuid.UUID,
    _user: CurrentUser = Depends(_admin_dep),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[AdminUserResponse]:
    service = AdminService(session)
    result = await service.freeze_user(actor_id)
    return ApiResponse(success=True, data=result)


@router.patch("/projects/{project_id}/hide")  # type: ignore[untyped-decorator]
async def hide_project(
    project_id: uuid.UUID,
    _user: CurrentUser = Depends(_admin_dep),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[AdminProjectResponse]:
    service = AdminService(session)
    result = await service.hide_project(project_id)
    return ApiResponse(success=True, data=result)
