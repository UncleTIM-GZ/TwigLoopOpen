"""DeliveryEvidence repository — data access for delivery_evidences table."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.delivery_evidence import DeliveryEvidence


class EvidenceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, evidence_id: uuid.UUID) -> DeliveryEvidence | None:
        stmt = select(DeliveryEvidence).where(DeliveryEvidence.id == evidence_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_task(self, task_id: uuid.UUID) -> list[DeliveryEvidence]:
        stmt = (
            select(DeliveryEvidence)
            .where(DeliveryEvidence.task_id == task_id)
            .order_by(DeliveryEvidence.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_task(self, task_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(DeliveryEvidence)
            .where(DeliveryEvidence.task_id == task_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def find_latest_by_task(self, task_id: uuid.UUID) -> DeliveryEvidence | None:
        stmt = (
            select(DeliveryEvidence)
            .where(DeliveryEvidence.task_id == task_id, DeliveryEvidence.is_latest.is_(True))
            .order_by(DeliveryEvidence.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, evidence: DeliveryEvidence) -> DeliveryEvidence:
        self._session.add(evidence)
        await self._session.flush()
        return evidence

    async def update_fields(
        self, evidence: DeliveryEvidence, updates: dict[str, object]
    ) -> DeliveryEvidence:
        for key, value in updates.items():
            setattr(evidence, key, value)
        await self._session.flush()
        await self._session.refresh(evidence)
        return evidence
