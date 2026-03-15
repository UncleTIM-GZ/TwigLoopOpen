"""Signal service — business logic for project signals."""

import uuid
from datetime import datetime
from typing import Any

from shared_events import Subjects, publish_event
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.signal import ProjectSignal
from app.repositories.signal_repo import SignalRepository
from app.schemas.signal import SignalResponse


class SignalService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = SignalRepository(session)

    async def create_signal(
        self,
        *,
        project_id: uuid.UUID,
        signal_type: str,
        source_type: str,
        source_ref: str | None = None,
        payload: dict[str, Any] | None = None,
        occurred_at: datetime,
    ) -> SignalResponse:
        signal = ProjectSignal(
            project_id=project_id,
            signal_type=signal_type,
            source_type=source_type,
            source_ref=source_ref,
            payload_json=payload,
            occurred_at=occurred_at,
        )
        signal = await self._repo.create(signal)
        await publish_event(
            Subjects.SOURCE_SIGNAL_RECEIVED,
            {
                "signal_id": str(signal.id),
                "project_id": str(project_id),
                "signal_type": signal_type,
            },
        )
        return self._to_response(signal)

    async def list_by_project(
        self, project_id: uuid.UUID, *, limit: int = 50
    ) -> list[SignalResponse]:
        signals = await self._repo.find_by_project(project_id, limit=limit)
        return [self._to_response(s) for s in signals]

    @staticmethod
    def _to_response(signal: ProjectSignal) -> SignalResponse:
        return SignalResponse(
            signal_id=signal.id,
            project_id=signal.project_id,
            signal_type=signal.signal_type,
            source_type=signal.source_type,
            source_ref=signal.source_ref,
            payload_json=signal.payload_json,
            occurred_at=signal.occurred_at,
        )
