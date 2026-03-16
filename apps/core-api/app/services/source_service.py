"""Source service — business logic for project source bindings."""

import uuid

from shared_auth import CurrentUser
from shared_events import Subjects, publish_event
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.source import ProjectSource
from app.repositories.project_repo import ProjectRepository
from app.repositories.source_repo import SourceRepository
from app.schemas.source import BindRepoRequest, SourceResponse


class SourceService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = SourceRepository(session)
        self._project_repo = ProjectRepository(session)

    async def bind_repo(
        self, project_id: uuid.UUID, req: BindRepoRequest, user: CurrentUser
    ) -> SourceResponse:
        project = await self._project_repo.find_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        if project.founder_actor_id != user.actor_id:
            raise ForbiddenError("Only the project owner can bind sources")

        existing = await self._repo.find_by_repo_url(req.repo_url)
        if existing and existing.project_id == project_id:
            raise ConflictError("This repo is already bound to the project")

        source = ProjectSource(
            project_id=project_id,
            source_type=req.source_type,
            repo_url=req.repo_url,
            binding_status="active",
            external_repo_id=req.external_repo_id,
        )
        source = await self._repo.create(source)
        await publish_event(
            Subjects.SOURCE_BOUND,
            {"source_id": str(source.id), "project_id": str(project_id), "repo_url": req.repo_url},
            actor_id=user.actor_id,
        )
        return self._to_response(source)

    async def unbind_repo(self, source_id: uuid.UUID, user: CurrentUser) -> None:
        source = await self._repo.find_by_id(source_id)
        if not source:
            raise NotFoundError("Source not found")

        project = await self._project_repo.find_by_id(source.project_id)
        if not project or project.founder_actor_id != user.actor_id:
            raise ForbiddenError("Only the project owner can unbind sources")

        await self._repo.delete(source)
        await publish_event(
            Subjects.SOURCE_UNBOUND,
            {"source_id": str(source_id), "project_id": str(source.project_id)},
            actor_id=user.actor_id,
        )

    async def list_sources(self, project_id: uuid.UUID) -> list[SourceResponse]:
        sources = await self._repo.find_by_project(project_id)
        return [self._to_response(s) for s in sources]

    async def find_project_by_repo_url(self, repo_url: str) -> ProjectSource | None:
        return await self._repo.find_by_repo_url(repo_url)

    @staticmethod
    def _to_response(source: ProjectSource) -> SourceResponse:
        return SourceResponse(
            source_id=source.id,
            project_id=source.project_id,
            source_type=source.source_type,
            repo_url=source.repo_url,
            binding_status=source.binding_status,
            external_repo_id=source.external_repo_id,
            created_at=source.created_at,
            updated_at=source.updated_at,
        )
