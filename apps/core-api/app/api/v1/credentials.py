"""Verifiable Credential routes — issue, get, verify, revoke, status."""

import uuid

from fastapi import APIRouter, Depends
from shared_auth import CurrentUser, get_current_user
from shared_schemas import ApiResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.rate_limit import public_rate_limit
from app.schemas.credential import (
    CredentialHistoryEntry,
    CredentialResponse,
    CredentialStatusResponse,
    IssueCredentialRequest,
    RevokeCredentialRequest,
    SuspendCredentialRequest,
    VerifyResponse,
)
from app.services.vc_service import VerifiableCredentialService

router = APIRouter(prefix="/credentials", tags=["credentials"])


@router.post("/issue", status_code=201)  # type: ignore[untyped-decorator]
async def issue_credential(
    body: IssueCredentialRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[CredentialResponse]:
    service = VerifiableCredentialService(session)
    result = await service.issue(body, user)
    return ApiResponse(success=True, data=result)


@router.post("/{vc_id}/revoke")  # type: ignore[untyped-decorator]
async def revoke_credential(
    vc_id: uuid.UUID,
    body: RevokeCredentialRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[CredentialStatusResponse]:
    """Revoke an issued credential."""
    service = VerifiableCredentialService(session)
    result = await service.revoke(vc_id, body, user)
    return ApiResponse(success=True, data=result)


@router.post("/{vc_id}/suspend")  # type: ignore[untyped-decorator]
async def suspend_credential(
    vc_id: uuid.UUID,
    body: SuspendCredentialRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[CredentialStatusResponse]:
    """Suspend an issued credential (reversible)."""
    service = VerifiableCredentialService(session)
    result = await service.suspend(vc_id, body, user)
    return ApiResponse(success=True, data=result)


@router.post("/{vc_id}/reactivate")  # type: ignore[untyped-decorator]
async def reactivate_credential(
    vc_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[CredentialStatusResponse]:
    """Reactivate a suspended credential."""
    service = VerifiableCredentialService(session)
    result = await service.reactivate(vc_id, user)
    return ApiResponse(success=True, data=result)


@router.get("/{vc_id}/status", dependencies=[Depends(public_rate_limit)])  # type: ignore[untyped-decorator]
async def get_credential_status(
    vc_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[CredentialStatusResponse]:
    """Get credential lifecycle status (public, no auth)."""
    service = VerifiableCredentialService(session)
    result = await service.get_status(vc_id)
    return ApiResponse(success=True, data=result)


@router.get("/verify/{vc_id}", dependencies=[Depends(public_rate_limit)])  # type: ignore[untyped-decorator]
async def verify_credential(
    vc_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[VerifyResponse]:
    service = VerifiableCredentialService(session)
    result = await service.verify(vc_id)
    return ApiResponse(success=True, data=result)


@router.get("/{vc_id}/history")  # type: ignore[untyped-decorator]
async def get_credential_history(
    vc_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[list[CredentialHistoryEntry]]:
    """Get credential lifecycle history (auth required)."""
    service = VerifiableCredentialService(session)
    result = await service.get_history(vc_id, user)
    return ApiResponse(success=True, data=result)


@router.get("/{vc_id}")  # type: ignore[untyped-decorator]
async def get_credential(
    vc_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiResponse[CredentialResponse]:
    service = VerifiableCredentialService(session)
    result = await service.get_by_id(vc_id, user)
    return ApiResponse(success=True, data=result)
