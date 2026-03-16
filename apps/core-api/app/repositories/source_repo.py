"""Source repository — data access for project_sources table."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.source import ProjectSource


class SourceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, source_id: uuid.UUID) -> ProjectSource | None:
        stmt = select(ProjectSource).where(ProjectSource.id == source_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_project(self, project_id: uuid.UUID) -> list[ProjectSource]:
        stmt = (
            select(ProjectSource)
            .where(ProjectSource.project_id == project_id)
            .order_by(ProjectSource.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_repo_url(self, repo_url: str) -> ProjectSource | None:
        stmt = select(ProjectSource).where(
            ProjectSource.repo_url == repo_url,
            ProjectSource.binding_status == "active",
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, source: ProjectSource) -> ProjectSource:
        self._session.add(source)
        await self._session.flush()
        return source

    async def delete(self, source: ProjectSource) -> None:
        await self._session.delete(source)
        await self._session.flush()
