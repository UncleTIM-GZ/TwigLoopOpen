"""Work package service."""

import logging
import uuid
from decimal import Decimal

from shared_auth import CurrentUser
from shared_schemas import PaginatedMeta
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ForbiddenError, NotFoundError
from app.models.work_package import WorkPackage
from app.repositories.project_repo import ProjectRepository
from app.repositories.task_card_repo import TaskCardRepository
from app.repositories.work_package_repo import WorkPackageRepository
from app.schemas.work_package import (
    CreateWorkPackageRequest,
    UpdateWorkPackageRequest,
    WorkPackageResponse,
)
from app.services.event_write_service import EventWriteService

logger = logging.getLogger(__name__)


class WorkPackageService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = WorkPackageRepository(session)
        self._project_repo = ProjectRepository(session)
        self._events = EventWriteService(session)

    async def create(
        self, project_id: uuid.UUID, req: CreateWorkPackageRequest, user: CurrentUser
    ) -> WorkPackageResponse:
        await self._check_owner(project_id, user)
        wp = WorkPackage(
            project_id=project_id,
            title=req.title,
            description=req.description,
            sort_order=req.sort_order,
        )
        wp = await self._repo.create(wp)

        try:
            await self._events.record_domain_event(
                "work_package_created",
                "work_package",
                wp.id,
                actor_id=user.actor_id,
            )
        except Exception:
            logger.warning(
                "Side-effect failed: work_package_created for wp=%s (actor=%s)",
                wp.id,
                user.actor_id,
                exc_info=True,
            )

        return self._to_response(wp)  # New WP has no tasks; defaults are fine

    async def get_by_project(self, project_id: uuid.UUID) -> list[WorkPackageResponse]:
        project = await self._project_repo.find_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        items = await self._repo.find_by_project(project_id)
        results = []
        for wp in items:
            agg = await self._aggregate_tasks(wp.id)
            results.append(self._to_response(wp, agg))
        return results

    async def get_list(
        self, project_id: uuid.UUID, *, page: int = 1, limit: int = 20
    ) -> tuple[list[WorkPackageResponse], PaginatedMeta]:
        project = await self._project_repo.find_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        offset = (page - 1) * limit
        items, total = await self._repo.find_paginated_by_project(
            project_id, offset=offset, limit=limit
        )
        meta = PaginatedMeta(
            total=total,
            page=page,
            limit=limit,
            has_next=(offset + limit) < total,
        )
        results = []
        for wp in items:
            agg = await self._aggregate_tasks(wp.id)
            results.append(self._to_response(wp, agg))
        return results, meta

    async def update(
        self, wp_id: uuid.UUID, req: UpdateWorkPackageRequest, user: CurrentUser
    ) -> WorkPackageResponse:
        wp = await self._repo.find_by_id(wp_id)
        if not wp:
            raise NotFoundError("Work package not found")
        await self._check_owner(wp.project_id, user)
        updates = req.model_dump(exclude_unset=True)
        allowed = {"title", "description", "sort_order"}
        updates = {k: v for k, v in updates.items() if k in allowed}
        wp = await self._repo.update_fields(wp, updates)
        agg = await self._aggregate_tasks(wp.id)
        return self._to_response(wp, agg)

    async def _check_owner(self, project_id: uuid.UUID, user: CurrentUser) -> None:
        project = await self._project_repo.find_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        if project.founder_actor_id != user.actor_id:
            raise ForbiddenError("Only the project owner can manage work packages")

    async def _aggregate_tasks(self, wp_id: uuid.UUID) -> dict[str, Decimal | int | None]:
        """Compute EWU/RWU/SWU aggregates from child task cards."""
        task_repo = TaskCardRepository(self._repo._session)
        tasks = await task_repo.find_by_work_package(wp_id)
        if not tasks:
            return {
                "total_ewu": Decimal("0"),
                "avg_ewu": None,
                "total_rwu": None,
                "total_swu": None,
                "task_count": 0,
            }
        total_ewu = Decimal(str(sum(t.ewu for t in tasks)))
        avg_ewu = (total_ewu / len(tasks)).quantize(Decimal("0.01"))
        rwu_sum = sum(t.rwu for t in tasks if t.rwu is not None)
        swu_sum = sum(t.swu for t in tasks if t.swu is not None)
        return {
            "total_ewu": total_ewu,
            "avg_ewu": avg_ewu,
            "total_rwu": Decimal(str(rwu_sum)) if rwu_sum else None,
            "total_swu": Decimal(str(swu_sum)) if swu_sum else None,
            "task_count": len(tasks),
        }

    @staticmethod
    def _to_response(
        wp: WorkPackage, agg: dict[str, Decimal | int | None] | None = None
    ) -> WorkPackageResponse:
        return WorkPackageResponse(
            work_package_id=wp.id,
            project_id=wp.project_id,
            title=wp.title,
            description=wp.description,
            status=wp.status,
            sort_order=wp.sort_order,
            created_at=wp.created_at,
            updated_at=wp.updated_at,
            total_ewu=agg["total_ewu"] if agg else Decimal("0"),  # type: ignore[arg-type]
            avg_ewu=agg["avg_ewu"] if agg else None,  # type: ignore[arg-type]
            total_rwu=agg["total_rwu"] if agg else None,  # type: ignore[arg-type]
            total_swu=agg["total_swu"] if agg else None,  # type: ignore[arg-type]
            task_count=agg["task_count"] if agg else 0,  # type: ignore[arg-type]
        )
