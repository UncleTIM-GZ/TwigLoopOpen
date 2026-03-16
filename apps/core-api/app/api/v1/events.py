"""Event routes — read-only access to domain events and state transitions."""

import uuid

from fastapi import APIRouter, Depends, Query
from shared_auth import CurrentUser, get_current_user
from shared_schemas import ApiResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.repositories.domain_event_repo import DomainEventRepository
from app.repositories.state_transition_repo import StateTransitionRepository
from app.schemas.event import DomainEventResponse, StateTransitionResponse

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/domain/{aggregate_type}/{aggregate_id}")  # type: ignore[untyped-decorator]
async def get_domain_events(
    aggregate_type: str,
    aggregate_id: uuid.UUID,
    limit: int = Query(default=50, le=200),
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[DomainEventResponse]]:
    """Get domain events for an aggregate. Requires authentication."""
    repo = DomainEventRepository(session)
    events = await repo.find_by_aggregate(aggregate_type, aggregate_id, limit=limit)
    return ApiResponse(
        success=True,
        data=[DomainEventResponse.model_validate(e, from_attributes=True) for e in events],
    )


@router.get("/transitions/{object_type}/{object_id}")  # type: ignore[untyped-decorator]
async def get_state_transitions(
    object_type: str,
    object_id: uuid.UUID,
    limit: int = Query(default=50, le=200),
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[StateTransitionResponse]]:
    """Get state transitions for an object. Requires authentication."""
    repo = StateTransitionRepository(session)
    events = await repo.find_by_object(object_type, object_id, limit=limit)
    return ApiResponse(
        success=True,
        data=[StateTransitionResponse.model_validate(e, from_attributes=True) for e in events],
    )
