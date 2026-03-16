"""FastAPI authentication dependencies."""

from collections.abc import Callable
from typing import Any

import jwt as pyjwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from shared_auth.jwt import decode_token, token_to_current_user
from shared_auth.types import CurrentUser

_bearer_scheme = HTTPBearer(auto_error=False)

_ACCESS_COOKIE = "twigloop_access_token"


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> CurrentUser:
    """Extract and validate the current user.

    Token resolution order (dual-track auth):
    1. Authorization: Bearer <token> header (MCP / API clients)
    2. httpOnly cookie ``twigloop_access_token`` (browser clients)
    """
    token: str | None = None

    # 1. Try Authorization header first
    if credentials is not None:
        token = credentials.credentials

    # 2. Fallback to httpOnly cookie
    if token is None:
        token = request.cookies.get(_ACCESS_COOKIE)

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        payload = decode_token(token)
    except pyjwt.InvalidTokenError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from err
    if payload.token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    return token_to_current_user(payload)


def require_role(*roles: str) -> Callable[..., Any]:
    """Return a dependency that checks the user has at least one of the given roles."""

    async def _check(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not any(r in user.roles for r in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return _check
