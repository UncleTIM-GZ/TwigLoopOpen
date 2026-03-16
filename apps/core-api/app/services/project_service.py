"""Project service — business logic for project CRUD."""

import uuid
from decimal import Decimal

from shared_auth import CurrentUser
from shared_events import Subjects, publish_event
from shared_schemas import PaginatedMeta
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.state_machine import validate_project_transition
from app.exceptions import ForbiddenError, NotFoundError
from app.models.project import Project
from app.repositories.project_repo import ProjectRepository
from app.repositories.task_card_repo import TaskCardRepository
from app.schemas.project import (
    CreateProjectRequest,
    ProjectListParams,
    ProjectResponse,
    UpdateProjectRequest,
)
from app.services.event_write_service import EventWriteService
from app.services.relation_edge_service import RelationEdgeService


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = ProjectRepository(session)
        self._events = EventWriteService(session)
        self._edges = RelationEdgeService(session)

    async def create(self, req: CreateProjectRequest, user: CurrentUser) -> ProjectResponse:
        if "founder" not in user.roles:
            raise ForbiddenError("Only founders can create projects")

        needs_reviewer = req.project_type == "public_benefit"
        review_status = "reviewer_required" if needs_reviewer else "none"

        project = Project(
            founder_actor_id=user.actor_id,
            project_type=req.project_type,
            founder_type=req.founder_type,
            title=req.title,
            summary=req.summary,
            target_users=req.target_users,
            current_stage=req.current_stage,
            min_start_step=req.min_start_step,
            status="draft",
            needs_human_reviewer=needs_reviewer,
            human_review_status=review_status,
            has_reward=req.project_type == "recruitment",
            has_sponsor=False,
            created_via=req.created_via,
        )
        project = await self._repo.create(project)
        await publish_event(
            Subjects.PROJECT_CREATED,
            {"project_id": str(project.id), "title": project.title},
            actor_id=user.actor_id,
        )

        try:
            await self._events.record_domain_event(
                "project_created",
                "project",
                project.id,
                actor_id=user.actor_id,
                payload={"title": project.title},
            )
            await self._events.record_state_transition(
                "project",
                project.id,
                None,
                "draft",
                trigger_actor_id=user.actor_id,
            )
            await self._edges.create_actor_project_edge(
                user.actor_id,
                project.id,
                "founded",
            )
        except Exception:
            pass  # Event write failure should not block business logic during transition

        return self._to_response(project)

    async def get_by_id(self, project_id: uuid.UUID) -> ProjectResponse:
        project = await self._repo.find_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        agg = await self._aggregate_tasks(project.id)
        return self._to_response(project, agg)

    async def get_list(
        self, params: ProjectListParams
    ) -> tuple[list[ProjectResponse], PaginatedMeta]:
        offset = (params.page - 1) * params.limit
        items, total = await self._repo.find_list(
            project_type=params.project_type,
            status=params.status,
            offset=offset,
            limit=params.limit,
        )
        meta = PaginatedMeta(
            total=total,
            page=params.page,
            limit=params.limit,
            has_next=(offset + params.limit) < total,
        )
        results = []
        for p in items:
            agg = await self._aggregate_tasks(p.id)
            results.append(self._to_response(p, agg))
        return results, meta

    async def update(
        self, project_id: uuid.UUID, req: UpdateProjectRequest, user: CurrentUser
    ) -> ProjectResponse:
        project = await self._repo.find_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        if project.founder_actor_id != user.actor_id:
            raise ForbiddenError("Only the project owner can update")

        updates = req.model_dump(exclude_unset=True)
        project = await self._repo.update_fields(project, updates)
        agg = await self._aggregate_tasks(project.id)
        return self._to_response(project, agg)

    async def transition_status(
        self, project_id: uuid.UUID, target_status: str, user: CurrentUser
    ) -> ProjectResponse:
        project = await self._repo.find_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        if project.founder_actor_id != user.actor_id:
            raise ForbiddenError("Only the project owner can change status")
        old_status = project.status
        validate_project_transition(old_status, target_status)
        project = await self._repo.update_fields(project, {"status": target_status})

        try:
            await self._events.record_domain_event(
                "project_status_changed",
                "project",
                project.id,
                actor_id=user.actor_id,
            )
            await self._events.record_state_transition(
                "project",
                project.id,
                old_status,
                target_status,
                trigger_actor_id=user.actor_id,
            )
        except Exception:
            pass  # Event write failure should not block business logic during transition

        agg = await self._aggregate_tasks(project.id)
        return self._to_response(project, agg)

    async def _aggregate_tasks(self, project_id: uuid.UUID) -> dict[str, Decimal | int | None]:
        """Compute EWU/RWU/SWU aggregates from all task cards in the project."""
        task_repo = TaskCardRepository(self._repo._session)
        tasks = await task_repo.find_by_project(project_id)
        if not tasks:
            return {
                "total_ewu": Decimal("0"),
                "avg_ewu": None,
                "max_ewu": None,
                "total_rwu": None,
                "total_swu": None,
                "task_count": 0,
            }
        total_ewu = Decimal(str(sum(t.ewu for t in tasks)))
        avg_ewu = (total_ewu / len(tasks)).quantize(Decimal("0.01"))
        max_ewu = max(t.ewu for t in tasks)
        rwu_sum = sum(t.rwu for t in tasks if t.rwu is not None)
        swu_sum = sum(t.swu for t in tasks if t.swu is not None)
        return {
            "total_ewu": total_ewu,
            "avg_ewu": avg_ewu,
            "max_ewu": max_ewu,
            "total_rwu": Decimal(str(rwu_sum)) if rwu_sum else None,
            "total_swu": Decimal(str(swu_sum)) if swu_sum else None,
            "task_count": len(tasks),
        }

    @staticmethod
    def _to_response(
        project: Project, agg: dict[str, Decimal | int | None] | None = None
    ) -> ProjectResponse:
        return ProjectResponse(
            project_id=project.id,
            founder_actor_id=project.founder_actor_id,
            project_type=project.project_type,
            founder_type=project.founder_type,
            title=project.title,
            summary=project.summary,
            target_users=project.target_users,
            current_stage=project.current_stage,
            min_start_step=project.min_start_step,
            status=project.status,
            needs_human_reviewer=project.needs_human_reviewer,
            human_review_status=project.human_review_status,
            has_reward=project.has_reward,
            has_sponsor=project.has_sponsor,
            created_via=project.created_via,
            created_at=project.created_at,
            updated_at=project.updated_at,
            total_ewu=agg["total_ewu"] if agg else Decimal("0"),  # type: ignore[arg-type]
            avg_ewu=agg["avg_ewu"] if agg else None,  # type: ignore[arg-type]
            max_ewu=agg["max_ewu"] if agg else None,  # type: ignore[arg-type]
            total_rwu=agg["total_rwu"] if agg else None,  # type: ignore[arg-type]
            total_swu=agg["total_swu"] if agg else None,  # type: ignore[arg-type]
            task_count=agg["task_count"] if agg else 0,  # type: ignore[arg-type]
        )
