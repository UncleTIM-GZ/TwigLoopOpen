"""Sponsor service — business logic for sponsor support management."""

from shared_auth import CurrentUser
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ForbiddenError, NotFoundError
from app.models.sponsor_support import SponsorSupport
from app.repositories.actor_repo import ActorRepository
from app.repositories.project_repo import ProjectRepository
from app.repositories.sponsor_support_repo import SponsorSupportRepository
from app.schemas.sponsor import CreateSupportRequest, SupportResponse


class SponsorService:
    def __init__(self, session: AsyncSession) -> None:
        self._actor_repo = ActorRepository(session)
        self._project_repo = ProjectRepository(session)
        self._support_repo = SponsorSupportRepository(session)

    async def create_support(self, req: CreateSupportRequest, user: CurrentUser) -> SupportResponse:
        """Create a new sponsor support for a project."""
        actor = await self._actor_repo.find_by_id(user.actor_id)
        if not actor or not actor.is_sponsor:
            raise ForbiddenError("Only sponsors can create support")

        project = await self._project_repo.find_by_id(req.project_id)
        if not project:
            raise NotFoundError("Project not found")

        support = SponsorSupport(
            project_id=req.project_id,
            sponsor_actor_id=user.actor_id,
            support_type=req.support_type,
            amount=req.amount,
            status="active",
        )
        support = await self._support_repo.create(support)

        # Mark project as having sponsor if not already
        if not project.has_sponsor:
            await self._project_repo.update_fields(project, {"has_sponsor": True})

        return self._to_response(support)

    async def list_my_supports(self, user: CurrentUser) -> list[SupportResponse]:
        """List all supports by the current sponsor."""
        actor = await self._actor_repo.find_by_id(user.actor_id)
        if not actor or not actor.is_sponsor:
            raise ForbiddenError("Only sponsors can view their supports")

        items = await self._support_repo.find_by_sponsor(user.actor_id)
        return [self._to_response(s) for s in items]

    @staticmethod
    def _to_response(support: SponsorSupport) -> SupportResponse:
        return SupportResponse(
            support_id=support.id,
            project_id=support.project_id,
            sponsor_actor_id=support.sponsor_actor_id,
            support_type=support.support_type,
            amount=support.amount,
            status=support.status,
            created_at=support.created_at,
        )
