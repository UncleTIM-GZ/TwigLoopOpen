"""User profile routes — GET/PATCH /me."""

from fastapi import APIRouter, Depends, Query
from shared_auth import CurrentUser, get_current_user
from shared_schemas import ApiResponse, PaginatedMeta
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.application import ProjectApplication
from app.models.seat import ProjectSeat
from app.models.task_card import TaskCard
from app.models.work_package import WorkPackage
from app.schemas.application import ApplicationResponse
from app.schemas.credential import CredentialResponse
from app.schemas.task_card import TaskCardResponse
from app.schemas.user import ActorInfo, MeResponse, UpdateProfileRequest
from app.services.profile_service import ProfileService
from app.services.vc_service import VerifiableCredentialService

router = APIRouter(tags=["me"])


@router.get("/me")  # type: ignore[untyped-decorator]
async def get_me(
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[MeResponse]:
    service = ProfileService(session)
    result = await service.get_profile(user)
    return ApiResponse(success=True, data=result)


@router.patch("/me")  # type: ignore[untyped-decorator]
async def update_me(
    body: UpdateProfileRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ActorInfo]:
    service = ProfileService(session)
    result = await service.update_profile(user, body)
    return ApiResponse(success=True, data=result)


@router.get("/me/credentials")  # type: ignore[untyped-decorator]
async def list_my_credentials(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[CredentialResponse]]:
    service = VerifiableCredentialService(session)
    results, meta = await service.get_list_for_actor(user, page=page, limit=limit)
    return ApiResponse(success=True, data=results, meta=meta.model_dump())


@router.get("/me/tasks")  # type: ignore[untyped-decorator]
async def list_my_tasks(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[TaskCardResponse]]:
    """List tasks assigned to the current user via their seats."""
    # Base condition: projects where user has an active/trial seat
    seat_filter = (
        select(WorkPackage.id)
        .join(ProjectSeat, ProjectSeat.project_id == WorkPackage.project_id)
        .where(ProjectSeat.actor_id == user.actor_id)
        .where(ProjectSeat.status.in_(["on_trial", "active"]))
    )

    # Count query
    count_stmt = select(func.count()).where(TaskCard.work_package_id.in_(seat_filter))
    total = (await session.execute(count_stmt)).scalar_one()

    # Data query
    stmt = (
        select(TaskCard)
        .where(TaskCard.work_package_id.in_(seat_filter))
        .order_by(TaskCard.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    rows = (await session.execute(stmt)).scalars().all()

    results = [
        TaskCardResponse(
            task_id=t.id,
            work_package_id=t.work_package_id,
            title=t.title,
            task_type=t.task_type,
            goal=t.goal,
            input_conditions=t.input_conditions,
            output_spec=t.output_spec,
            completion_criteria=t.completion_criteria,
            main_role=t.main_role,
            risk_level=t.risk_level,
            status=t.status,
            ewu=t.ewu,
            rwu=t.rwu,
            swu=t.swu,
            has_reward=t.has_reward,
            verification_status=t.verification_status,
            completion_mode=t.completion_mode,
            signal_count=t.signal_count,
            created_at=t.created_at,
            updated_at=t.updated_at,
        )
        for t in rows
    ]

    meta = PaginatedMeta(total=total, page=page, limit=limit, has_next=(page * limit < total))
    return ApiResponse(success=True, data=results, meta=meta.model_dump())


@router.get("/me/applications")  # type: ignore[untyped-decorator]
async def list_my_applications(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ApplicationResponse]]:
    """List the current user's project applications."""
    # Count query
    count_stmt = (
        select(func.count())
        .select_from(ProjectApplication)
        .where(ProjectApplication.actor_id == user.actor_id)
    )
    total = (await session.execute(count_stmt)).scalar_one()

    # Data query
    stmt = (
        select(ProjectApplication)
        .where(ProjectApplication.actor_id == user.actor_id)
        .order_by(ProjectApplication.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    rows = (await session.execute(stmt)).scalars().all()

    results = [
        ApplicationResponse(
            application_id=a.id,
            project_id=a.project_id,
            actor_id=a.actor_id,
            seat_preference=a.seat_preference,
            intended_role=a.intended_role,
            motivation=a.motivation,
            availability=a.availability,
            status=a.status,
            created_at=a.created_at,
            updated_at=a.updated_at,
            reviewed_at=a.reviewed_at,
        )
        for a in rows
    ]

    meta = PaginatedMeta(total=total, page=page, limit=limit, has_next=(page * limit < total))
    return ApiResponse(success=True, data=results, meta=meta.model_dump())
