"""Graph routes — read-only access to edges and feature snapshots."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from shared_auth import CurrentUser, get_current_user
from shared_schemas import ApiResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.repositories.edge_repo import ActorActorEdgeRepository, ActorProjectEdgeRepository
from app.repositories.snapshot_repo import (
    ActorFeatureSnapshotRepository,
    ProjectFeatureSnapshotRepository,
)
from app.schemas.graph import (
    ActorActorEdgeResponse,
    ActorFeatureSnapshotResponse,
    ActorProjectEdgeResponse,
    ProjectFeatureSnapshotResponse,
)

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/edges/actor-project")  # type: ignore[untyped-decorator]
async def get_actor_project_edges(
    actor_id: uuid.UUID | None = None,
    project_id: uuid.UUID | None = None,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ActorProjectEdgeResponse]]:
    """Get actor-project edges, filter by actor or project."""
    repo = ActorProjectEdgeRepository(session)
    if actor_id:
        edges = await repo.find_by_actor(actor_id)
    elif project_id:
        edges = await repo.find_by_project(project_id)
    else:
        raise HTTPException(status_code=400, detail="Provide actor_id or project_id")
    return ApiResponse(
        success=True,
        data=[ActorProjectEdgeResponse.model_validate(e, from_attributes=True) for e in edges],
    )


@router.get("/edges/actor-actor")  # type: ignore[untyped-decorator]
async def get_actor_actor_edges(
    actor_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[ActorActorEdgeResponse]]:
    """Get actor-actor edges for a given actor."""
    repo = ActorActorEdgeRepository(session)
    edges = await repo.find_by_actor(actor_id)
    return ApiResponse(
        success=True,
        data=[ActorActorEdgeResponse.model_validate(e, from_attributes=True) for e in edges],
    )


@router.get("/snapshots/actors/{actor_id}")  # type: ignore[untyped-decorator]
async def get_actor_snapshot(
    actor_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ActorFeatureSnapshotResponse]:
    """Get the latest feature snapshot for an actor."""
    repo = ActorFeatureSnapshotRepository(session)
    snapshot = await repo.find_latest(actor_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="No snapshot found")
    return ApiResponse(
        success=True,
        data=ActorFeatureSnapshotResponse.model_validate(snapshot, from_attributes=True),
    )


@router.get("/snapshots/projects/{project_id}")  # type: ignore[untyped-decorator]
async def get_project_snapshot(
    project_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[ProjectFeatureSnapshotResponse]:
    """Get the latest feature snapshot for a project."""
    repo = ProjectFeatureSnapshotRepository(session)
    snapshot = await repo.find_latest(project_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="No snapshot found")
    return ApiResponse(
        success=True,
        data=ProjectFeatureSnapshotResponse.model_validate(snapshot, from_attributes=True),
    )
