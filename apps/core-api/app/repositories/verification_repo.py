"""TaskVerification repository — data access for task_verifications table."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task_verification import TaskVerification


class VerificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, verification_id: uuid.UUID) -> TaskVerification | None:
        stmt = select(TaskVerification).where(TaskVerification.id == verification_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_task(self, task_id: uuid.UUID) -> list[TaskVerification]:
        stmt = (
            select(TaskVerification)
            .where(TaskVerification.task_id == task_id)
            .order_by(TaskVerification.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, verification: TaskVerification) -> TaskVerification:
        self._session.add(verification)
        await self._session.flush()
        return verification
