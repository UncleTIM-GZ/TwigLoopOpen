"""Auth routes — register, login, refresh, and logout."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from shared_schemas import ApiResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.rate_limit import auth_rate_limit
from app.schemas.auth import AuthResponse, LoginRequest, RefreshTokenRequest, RegisterRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

# Cookie configuration constants
_ACCESS_COOKIE = "twigloop_access_token"
_REFRESH_COOKIE = "twigloop_refresh_token"
_ACCESS_MAX_AGE = 3600  # 1 hour
_REFRESH_MAX_AGE = 86400 * 7  # 7 days


def _set_auth_cookies(response: JSONResponse, result: AuthResponse) -> None:
    """Set httpOnly auth cookies on the response (for browser clients)."""
    response.set_cookie(
        key=_ACCESS_COOKIE,
        value=result.access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=_ACCESS_MAX_AGE,
        path="/",
    )
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=result.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=_REFRESH_MAX_AGE,
        path="/api/v1/auth",  # only sent to auth endpoints
    )


def _auth_json_response(result: AuthResponse, *, status_code: int = 200) -> JSONResponse:
    """Build a JSONResponse with both JSON body and httpOnly cookies."""
    envelope = ApiResponse(success=True, data=result)
    response = JSONResponse(
        content=envelope.model_dump(mode="json"),
        status_code=status_code,
    )
    _set_auth_cookies(response, result)
    return response


@router.post("/register", status_code=201, dependencies=[Depends(auth_rate_limit)])  # type: ignore[untyped-decorator]
async def register(
    body: RegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> JSONResponse:
    service = AuthService(session)
    result = await service.register(body)
    return _auth_json_response(result, status_code=201)


@router.post("/login", dependencies=[Depends(auth_rate_limit)])  # type: ignore[untyped-decorator]
async def login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> JSONResponse:
    service = AuthService(session)
    result = await service.login(body)
    return _auth_json_response(result)


@router.post("/refresh", dependencies=[Depends(auth_rate_limit)])  # type: ignore[untyped-decorator]
async def refresh_token(
    body: RefreshTokenRequest,
    session: AsyncSession = Depends(get_session),
) -> JSONResponse:
    service = AuthService(session)
    result = await service.refresh(body)
    return _auth_json_response(result)


@router.post("/logout")  # type: ignore[untyped-decorator]
async def logout() -> JSONResponse:
    """Clear httpOnly auth cookies (browser logout)."""
    response = JSONResponse(
        content={"success": True, "data": None, "error": None, "meta": None},
    )
    response.delete_cookie(_ACCESS_COOKIE, path="/")
    response.delete_cookie(_REFRESH_COOKIE, path="/api/v1/auth")
    return response
