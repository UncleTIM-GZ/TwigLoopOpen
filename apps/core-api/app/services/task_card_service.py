"""Task card service."""

import logging
import uuid

from shared_auth import CurrentUser
from shared_schemas import PaginatedMeta
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.ewu import EwuInput, EwuResult, calculate_ewu
from app.domain.quota_config import MAX_EWU_PER_TASK
from app.domain.rwu_swu import calculate_rwu, calculate_swu
from app.domain.state_machine import validate_task_transition
from app.exceptions import AppError, ConflictError, ForbiddenError, NotFoundError
from app.models.project import Project
from app.models.task_card import TaskCard
from app.repositories.project_repo import ProjectRepository
from app.repositories.task_card_repo import TaskCardRepository
from app.repositories.work_package_repo import WorkPackageRepository
from app.schemas.task_card import CreateTaskCardRequest, TaskCardResponse, UpdateTaskCardRequest
from app.services.event_write_service import EventWriteService

logger = logging.getLogger(__name__)


class TaskCardService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = TaskCardRepository(session)
        self._wp_repo = WorkPackageRepository(session)
        self._project_repo = ProjectRepository(session)
        self._events = EventWriteService(session)

    async def create(
        self, wp_id: uuid.UUID, req: CreateTaskCardRequest, user: CurrentUser
    ) -> TaskCardResponse:
        wp = await self._wp_repo.find_by_id(wp_id)
        if not wp:
            raise NotFoundError("Work package not found")
        project = await self._check_owner(wp.project_id, user)

        if req.ewu is not None and req.ewu > MAX_EWU_PER_TASK:
            raise AppError(
                f"Task EWU {req.ewu} exceeds platform limit of {MAX_EWU_PER_TASK}",
                status_code=422,
            )

        # Determine project type for RWU/SWU calculation
        rwu_value = None
        swu_value = None
        has_reward = False
        if project:
            has_reward = project.has_reward
            if project.has_reward and req.ewu:
                rwu_value = calculate_rwu(req.ewu).rwu
            if project.has_sponsor and req.ewu:
                swu_value = calculate_swu(req.ewu).swu

        task = TaskCard(
            work_package_id=wp_id,
            title=req.title,
            task_type=req.task_type,
            goal=req.goal,
            input_conditions=req.input_conditions,
            output_spec=req.output_spec,
            completion_criteria=req.completion_criteria,
            main_role=req.main_role,
            risk_level=req.risk_level,
            ewu=req.ewu,
            rwu=rwu_value,
            swu=swu_value,
            has_reward=has_reward,
        )
        task = await self._repo.create(task)

        try:
            await self._events.record_domain_event(
                "task_created",
                "task",
                task.id,
                actor_id=user.actor_id,
            )
        except Exception:
            logger.warning(
                "Side-effect failed: task_created for task=%s (actor=%s)",
                task.id,
                user.actor_id,
                exc_info=True,
            )

        return self._to_response(task)

    async def get_by_project(self, project_id: uuid.UUID) -> list[TaskCardResponse]:
        project = await self._project_repo.find_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        items = await self._repo.find_by_project(project_id)
        return [self._to_response(t) for t in items]

    async def get_list(
        self, project_id: uuid.UUID, *, page: int = 1, limit: int = 20
    ) -> tuple[list[TaskCardResponse], PaginatedMeta]:
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
        return [self._to_response(t) for t in items], meta

    async def update(
        self, task_id: uuid.UUID, req: UpdateTaskCardRequest, user: CurrentUser
    ) -> TaskCardResponse:
        task = await self._repo.find_by_id(task_id)
        if not task:
            raise NotFoundError("Task not found")
        wp = await self._wp_repo.find_by_id(task.work_package_id)
        if not wp:
            raise NotFoundError("Work package not found")
        await self._check_owner(wp.project_id, user)

        if task.status in ("completed", "closed"):
            raise ConflictError("Cannot modify a task in terminal state")

        updates = req.model_dump(exclude_unset=True)
        allowed = {"title", "goal", "output_spec", "completion_criteria", "ewu"}
        updates = {k: v for k, v in updates.items() if k in allowed}

        # Recalculate RWU/SWU when EWU changes
        if "ewu" in updates and updates["ewu"] is not None:
            if updates["ewu"] > MAX_EWU_PER_TASK:
                raise AppError(
                    f"Task EWU {updates['ewu']} exceeds platform limit of {MAX_EWU_PER_TASK}",
                    status_code=422,
                )
            project = await self._project_repo.find_by_id(wp.project_id)
            if project and project.has_reward:
                updates["rwu"] = calculate_rwu(updates["ewu"]).rwu
            if project and project.has_sponsor:
                updates["swu"] = calculate_swu(updates["ewu"]).swu

        task = await self._repo.update_fields(task, updates)
        return self._to_response(task)

    async def transition_status(
        self, task_id: uuid.UUID, target_status: str, user: CurrentUser
    ) -> TaskCardResponse:
        task = await self._repo.find_by_id_for_update(task_id)
        if not task:
            raise NotFoundError("Task not found")
        wp = await self._wp_repo.find_by_id(task.work_package_id)
        if not wp:
            raise NotFoundError("Work package not found")
        await self._check_owner(wp.project_id, user)
        old_status = task.status
        validate_task_transition(old_status, target_status)
        task = await self._repo.update_fields(task, {"status": target_status})

        try:
            await self._events.record_domain_event(
                "task_status_changed",
                "task",
                task.id,
                actor_id=user.actor_id,
            )
            await self._events.record_state_transition(
                "task",
                task.id,
                old_status,
                target_status,
                trigger_actor_id=user.actor_id,
            )
        except Exception:
            logger.warning(
                "Side-effect failed: task_status_changed for task=%s (actor=%s)",
                task.id,
                user.actor_id,
                exc_info=True,
            )

        return self._to_response(task)

    async def calculate_ewu(
        self, task_id: uuid.UUID, params: EwuInput, user: CurrentUser
    ) -> EwuResult:
        task = await self._repo.find_by_id(task_id)
        if not task:
            raise NotFoundError("Task not found")
        wp = await self._wp_repo.find_by_id(task.work_package_id)
        if not wp:
            raise NotFoundError("Work package not found")
        await self._check_owner(wp.project_id, user)
        try:
            result = calculate_ewu(params)
        except ValueError as err:
            raise AppError(str(err), status_code=422) from err
        if result.ewu > MAX_EWU_PER_TASK:
            raise AppError(
                f"Task EWU {result.ewu} exceeds platform limit of {MAX_EWU_PER_TASK}",
                status_code=422,
            )
        ewu_updates: dict[str, object] = {"ewu": result.ewu}
        project = await self._project_repo.find_by_id(wp.project_id)
        if project and project.has_reward:
            ewu_updates["rwu"] = calculate_rwu(result.ewu).rwu
        if project and project.has_sponsor:
            ewu_updates["swu"] = calculate_swu(result.ewu).swu
        await self._repo.update_fields(task, ewu_updates)
        return result

    async def _check_owner(self, project_id: uuid.UUID, user: CurrentUser) -> Project:
        project = await self._project_repo.find_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        if project.founder_actor_id != user.actor_id:
            raise ForbiddenError("Only the project owner can manage tasks")
        return project

    @staticmethod
    def _to_response(task: TaskCard) -> TaskCardResponse:
        return TaskCardResponse(
            task_id=task.id,
            work_package_id=task.work_package_id,
            title=task.title,
            task_type=task.task_type,
            goal=task.goal,
            input_conditions=task.input_conditions,
            output_spec=task.output_spec,
            completion_criteria=task.completion_criteria,
            main_role=task.main_role,
            risk_level=task.risk_level,
            status=task.status,
            ewu=task.ewu,
            rwu=task.rwu,
            swu=task.swu,
            has_reward=task.has_reward,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
