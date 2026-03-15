"""Application service — apply, review, create seats."""

import logging
import uuid
from datetime import UTC, datetime

from shared_auth import CurrentUser
from shared_events import Subjects, publish_event
from shared_schemas import PaginatedMeta
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.state_machine import validate_application_transition
from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.application import ProjectApplication
from app.models.seat import ProjectSeat
from app.repositories.application_repo import ApplicationRepository
from app.repositories.project_repo import ProjectRepository
from app.repositories.seat_repo import SeatRepository
from app.schemas.application import (
    ApplicationResponse,
    CreateApplicationRequest,
    ReviewApplicationRequest,
    SeatResponse,
)
from app.services.event_write_service import EventWriteService
from app.services.relation_edge_service import RelationEdgeService

logger = logging.getLogger(__name__)


class ApplicationService:
    def __init__(self, session: AsyncSession) -> None:
        self._app_repo = ApplicationRepository(session)
        self._seat_repo = SeatRepository(session)
        self._project_repo = ProjectRepository(session)
        self._events = EventWriteService(session)
        self._edges = RelationEdgeService(session)

    async def apply(
        self, project_id: uuid.UUID, req: CreateApplicationRequest, user: CurrentUser
    ) -> ApplicationResponse:
        project = await self._project_repo.find_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        if project.founder_actor_id == user.actor_id:
            raise ConflictError("Cannot apply to your own project")

        existing = await self._app_repo.find_existing(project_id, user.actor_id)
        if existing:
            raise ConflictError("Already applied to this project")

        app = ProjectApplication(
            project_id=project_id,
            actor_id=user.actor_id,
            seat_preference=req.seat_preference,
            intended_role=req.intended_role,
            motivation=req.motivation,
            availability=req.availability,
        )
        app = await self._app_repo.create(app)
        await publish_event(
            Subjects.APPLICATION_SUBMITTED,
            {"application_id": str(app.id), "project_id": str(project_id)},
            actor_id=user.actor_id,
        )

        try:
            await self._events.record_domain_event(
                "application_submitted",
                "application",
                app.id,
                actor_id=user.actor_id,
                payload={"project_id": str(project_id)},
            )
            await self._events.record_state_transition(
                "application",
                app.id,
                None,
                "submitted",
                trigger_actor_id=user.actor_id,
            )
            await self._edges.create_actor_project_edge(
                user.actor_id,
                project_id,
                "applied",
            )
        except Exception:
            logger.warning(
                "Side-effect failed: apply events for application=%s (actor=%s)",
                app.id,
                user.actor_id,
                exc_info=True,
            )

        return self._to_app_response(app)

    async def list_by_project(
        self, project_id: uuid.UUID, user: CurrentUser
    ) -> list[ApplicationResponse]:
        project = await self._project_repo.find_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        if project.founder_actor_id != user.actor_id:
            raise ForbiddenError("Only project owner can view applications")
        items = await self._app_repo.find_by_project(project_id)
        return [self._to_app_response(a) for a in items]

    async def get_list_by_project(
        self, project_id: uuid.UUID, user: CurrentUser, *, page: int = 1, limit: int = 20
    ) -> tuple[list[ApplicationResponse], PaginatedMeta]:
        project = await self._project_repo.find_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        if project.founder_actor_id != user.actor_id:
            raise ForbiddenError("Only project owner can view applications")
        offset = (page - 1) * limit
        items, total = await self._app_repo.find_paginated_by_project(
            project_id, offset=offset, limit=limit
        )
        meta = PaginatedMeta(
            total=total,
            page=page,
            limit=limit,
            has_next=(offset + limit) < total,
        )
        return [self._to_app_response(a) for a in items], meta

    async def review(
        self, app_id: uuid.UUID, req: ReviewApplicationRequest, user: CurrentUser
    ) -> ApplicationResponse:
        app = await self._app_repo.find_by_id_for_update(app_id)
        if not app:
            raise NotFoundError("Application not found")

        # Permission check BEFORE state validation — prevents status probing
        project = await self._project_repo.find_by_id(app.project_id)
        if not project:
            raise NotFoundError("Project not found")
        if project.founder_actor_id != user.actor_id:
            raise ForbiddenError("Only project owner can review applications")

        validate_application_transition(app.status, req.decision)
        old_status = app.status
        updates: dict[str, object] = {
            "status": req.decision,
            "reviewed_at": datetime.now(UTC),
        }
        app = await self._app_repo.update_fields(app, updates)

        event_subject = (
            Subjects.APPLICATION_ACCEPTED
            if req.decision in ("accepted", "converted_to_growth_seat")
            else Subjects.APPLICATION_REJECTED
        )
        await publish_event(
            event_subject,
            {"application_id": str(app.id), "project_id": str(app.project_id)},
            actor_id=user.actor_id,
        )

        seat_created = False
        if req.decision in ("accepted", "converted_to_growth_seat"):
            is_growth_conversion = req.decision == "converted_to_growth_seat"
            seat_type = "growth" if is_growth_conversion else app.seat_preference
            seat = ProjectSeat(
                project_id=app.project_id,
                actor_id=app.actor_id,
                seat_type=seat_type,
                role_needed=app.intended_role,
                status="on_trial",
                reward_enabled=project.has_reward,
            )
            await self._seat_repo.create(seat)
            seat_created = True

        try:
            await self._events.record_domain_event(
                "application_reviewed",
                "application",
                app.id,
                actor_id=user.actor_id,
            )
            await self._events.record_state_transition(
                "application",
                app.id,
                old_status,
                req.decision,
                trigger_actor_id=user.actor_id,
            )
            if seat_created:
                await self._edges.create_actor_project_edge(
                    app.actor_id,
                    app.project_id,
                    "joined",
                )
                await self._edges.create_actor_actor_edge(
                    project.founder_actor_id,
                    app.actor_id,
                    "founder_collaborator",
                    project_id=app.project_id,
                )
        except Exception:
            logger.warning(
                "Side-effect failed: review events for application=%s (actor=%s)",
                app.id,
                user.actor_id,
                exc_info=True,
            )

        return self._to_app_response(app)

    async def withdraw(self, app_id: uuid.UUID, user: CurrentUser) -> ApplicationResponse:
        app = await self._app_repo.find_by_id_for_update(app_id)
        if not app:
            raise NotFoundError("Application not found")
        if app.actor_id != user.actor_id:
            raise ForbiddenError("Only the applicant can withdraw")
        validate_application_transition(app.status, "withdrawn")

        old_status = app.status
        app = await self._app_repo.update_fields(app, {"status": "withdrawn"})

        await publish_event(
            Subjects.APPLICATION_WITHDRAWN,
            {"application_id": str(app.id), "project_id": str(app.project_id)},
            actor_id=user.actor_id,
        )

        try:
            await self._events.record_domain_event(
                "application_withdrawn",
                "application",
                app.id,
                actor_id=user.actor_id,
            )
            await self._events.record_state_transition(
                "application",
                app.id,
                old_status,
                "withdrawn",
                trigger_actor_id=user.actor_id,
            )
        except Exception:
            logger.warning(
                "Side-effect failed: withdraw events for application=%s (actor=%s)",
                app.id,
                user.actor_id,
                exc_info=True,
            )

        return self._to_app_response(app)

    async def list_seats(self, project_id: uuid.UUID, user: CurrentUser) -> list[SeatResponse]:
        project = await self._project_repo.find_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        items = await self._seat_repo.find_by_project(project_id)
        # Authorization: founder or seated actor can view seats
        is_founder = project.founder_actor_id == user.actor_id
        is_seated = any(s.actor_id == user.actor_id for s in items)
        if not is_founder and not is_seated:
            raise ForbiddenError("Only project members can view seats")
        return [self._to_seat_response(s) for s in items]

    async def get_list_seats(
        self, project_id: uuid.UUID, user: CurrentUser, *, page: int = 1, limit: int = 20
    ) -> tuple[list[SeatResponse], PaginatedMeta]:
        project = await self._project_repo.find_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        # Authorization check: need all seats for membership check
        all_seats = await self._seat_repo.find_by_project(project_id)
        is_founder = project.founder_actor_id == user.actor_id
        is_seated = any(s.actor_id == user.actor_id for s in all_seats)
        if not is_founder and not is_seated:
            raise ForbiddenError("Only project members can view seats")

        offset = (page - 1) * limit
        items, total = await self._seat_repo.find_paginated_by_project(
            project_id, offset=offset, limit=limit
        )
        meta = PaginatedMeta(
            total=total,
            page=page,
            limit=limit,
            has_next=(offset + limit) < total,
        )
        return [self._to_seat_response(s) for s in items], meta

    @staticmethod
    def _to_app_response(app: ProjectApplication) -> ApplicationResponse:
        return ApplicationResponse(
            application_id=app.id,
            project_id=app.project_id,
            actor_id=app.actor_id,
            seat_preference=app.seat_preference,
            intended_role=app.intended_role,
            motivation=app.motivation,
            availability=app.availability,
            status=app.status,
            created_at=app.created_at,
            updated_at=app.updated_at,
            reviewed_at=app.reviewed_at,
        )

    @staticmethod
    def _to_seat_response(seat: ProjectSeat) -> SeatResponse:
        return SeatResponse(
            seat_id=seat.id,
            project_id=seat.project_id,
            actor_id=seat.actor_id,
            seat_type=seat.seat_type,
            role_needed=seat.role_needed,
            status=seat.status,
            reward_enabled=seat.reward_enabled,
            created_at=seat.created_at,
            updated_at=seat.updated_at,
        )
