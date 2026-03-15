"""Task card repository."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task_card import TaskCard


class TaskCardRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, task_id: uuid.UUID) -> TaskCard | None:
        stmt = select(TaskCard).where(TaskCard.id == task_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id_for_update(self, task_id: uuid.UUID) -> TaskCard | None:
        """Lock the row for state change — prevents concurrent modifications."""
        stmt = select(TaskCard).where(TaskCard.id == task_id).with_for_update()
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_project(self, project_id: uuid.UUID) -> list[TaskCard]:
        """Find all tasks for a project (via work packages)."""
        from app.models.work_package import WorkPackage

        stmt = (
            select(TaskCard)
            .join(WorkPackage, TaskCard.work_package_id == WorkPackage.id)
            .where(WorkPackage.project_id == project_id)
            .order_by(TaskCard.created_at)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_paginated_by_project(
        self, project_id: uuid.UUID, *, offset: int = 0, limit: int = 20
    ) -> tuple[list[TaskCard], int]:
        """Return (items, total_count) for tasks in a project."""
        from app.models.work_package import WorkPackage

        base = (
            select(TaskCard)
            .join(WorkPackage, TaskCard.work_package_id == WorkPackage.id)
            .where(WorkPackage.project_id == project_id)
        )
        count_stmt = select(func.count()).select_from(base.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = base.order_by(TaskCard.created_at).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())
        return items, total

    async def find_by_work_package(self, wp_id: uuid.UUID) -> list[TaskCard]:
        stmt = (
            select(TaskCard).where(TaskCard.work_package_id == wp_id).order_by(TaskCard.created_at)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, task: TaskCard) -> TaskCard:
        self._session.add(task)
        await self._session.flush()
        return task

    async def update_fields(self, task: TaskCard, updates: dict[str, object]) -> TaskCard:
        for key, value in updates.items():
            setattr(task, key, value)
        await self._session.flush()
        await self._session.refresh(task)
        return task
