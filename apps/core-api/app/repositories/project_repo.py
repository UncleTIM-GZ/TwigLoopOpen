"""Project repository — data access for projects table."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, project_id: uuid.UUID) -> Project | None:
        stmt = select(Project).where(Project.id == project_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_list(
        self,
        *,
        project_type: str | None = None,
        status: str | None = None,
        human_review_status: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Project], int]:
        """Return (items, total_count) with optional filters."""
        stmt = select(Project)
        count_stmt = select(func.count()).select_from(Project)

        if project_type:
            stmt = stmt.where(Project.project_type == project_type)
            count_stmt = count_stmt.where(Project.project_type == project_type)
        if status:
            stmt = stmt.where(Project.status == status)
            count_stmt = count_stmt.where(Project.status == status)
        if human_review_status:
            stmt = stmt.where(Project.human_review_status == human_review_status)
            count_stmt = count_stmt.where(Project.human_review_status == human_review_status)

        stmt = stmt.order_by(Project.created_at.desc()).offset(offset).limit(limit)

        result = await self._session.execute(stmt)
        items = list(result.scalars().all())

        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        return items, total

    async def create(self, project: Project) -> Project:
        self._session.add(project)
        await self._session.flush()
        return project

    async def update_fields(self, project: Project, updates: dict[str, object]) -> Project:
        for key, value in updates.items():
            setattr(project, key, value)
        await self._session.flush()
        await self._session.refresh(project)
        return project
