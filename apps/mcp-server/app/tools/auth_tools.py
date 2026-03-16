"""MCP auth tools — register and authenticate actors via standard MCP protocol."""

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from app.clients.core_api import call_core_api


def register_auth_tools(mcp: FastMCP) -> None:
    """Register authentication tools on the MCP server."""

    @mcp.tool(
        title="Register Actor",
        annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=False, openWorldHint=False),
    )
    async def register_actor(
        email: str,
        password: str,
        display_name: str,
        entry_intent: str = "both",
    ) -> dict[str, Any]:
        """Register a new actor on Twig Loop.

        Args:
            email: Valid email address for the account.
            password: Password (8-128 characters).
            display_name: Display name for the actor (1-100 characters).
            entry_intent: One of "founder", "collaborator", or "both".
        """
        return await call_core_api(
            "POST",
            "/api/v1/auth/register",
            json_body={
                "email": email,
                "password": password,
                "display_name": display_name,
                "entry_intent": entry_intent,
            },
        )

    @mcp.tool(
        title="Authenticate Actor",
        annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False),
    )
    async def authenticate_actor(
        email: str,
        password: str,
    ) -> dict[str, Any]:
        """Authenticate (login) an actor on Twig Loop.

        Returns access token and actor profile on success.

        Args:
            email: Account email address.
            password: Account password.
        """
        return await call_core_api(
            "POST",
            "/api/v1/auth/login",
            json_body={"email": email, "password": password},
        )

    @mcp.tool(
        title="Get Actor Profile",
        annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False),
    )
    async def get_actor_profile(access_token: str) -> dict[str, Any]:
        """Get the current actor's profile.

        Args:
            access_token: JWT access token from authenticate_actor.
        """
        return await call_core_api("GET", "/api/v1/me", token=access_token)
