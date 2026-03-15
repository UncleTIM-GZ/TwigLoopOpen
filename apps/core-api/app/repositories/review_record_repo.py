"""Review record repository — data access for review_records table."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review_record import ReviewRecord


class ReviewRecordRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, record: ReviewRecord) -> ReviewRecord:
        self._session.add(record)
        await self._session.flush()
        return record

    async def find_by_project(self, project_id: uuid.UUID) -> list[ReviewRecord]:
        stmt = (
            select(ReviewRecord)
            .where(ReviewRecord.project_id == project_id)
            .order_by(ReviewRecord.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
