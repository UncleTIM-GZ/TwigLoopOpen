"""MCP project tools — CRUD and application via standard MCP protocol."""

import re
from typing import Any

from mcp.server.fastmcp import FastMCP

from app.clients.core_api import call_core_api

_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)


def _validate_uuid(value: str, name: str) -> None:
    """Raise ValueError if value is not a valid UUID."""
    if not _UUID_RE.match(value):
        raise ValueError(f"Invalid {name}: must be a UUID (got '{value}')")


def register_project_tools(mcp: FastMCP) -> None:
    """Register project tools on the MCP server."""

    @mcp.tool()
    async def list_projects(
        project_type: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> dict[str, Any]:
        """List open projects on Twig Loop.

        Args:
            project_type: Filter by type ("general", "public_benefit", "recruitment").
            page: Page number (starts at 1).
            limit: Items per page (1-100).
        """
        params: dict[str, str] = {"page": str(page), "limit": str(limit)}
        if project_type:
            params["project_type"] = project_type
        return await call_core_api("GET", "/api/v1/projects/", params=params)

    @mcp.tool()
    async def get_project(project_id: str) -> dict[str, Any]:
        """Get detailed information about a specific project.

        Args:
            project_id: UUID of the project.
        """
        _validate_uuid(project_id, "project_id")
        return await call_core_api("GET", f"/api/v1/projects/{project_id}")

    @mcp.tool()
    async def create_project(
        access_token: str,
        project_type: str,
        founder_type: str,
        title: str,
        summary: str,
        target_users: str | None = None,
    ) -> dict[str, Any]:
        """Create a new project on Twig Loop.

        Args:
            access_token: JWT access token.
            project_type: One of "general", "public_benefit", "recruitment".
            founder_type: One of "individual", "organization", "contributor".
            title: Project title.
            summary: Brief description of the project.
            target_users: Who this project serves (optional).
        """
        return await call_core_api(
            "POST",
            "/api/v1/projects/",
            token=access_token,
            json_body={
                "project_type": project_type,
                "founder_type": founder_type,
                "title": title,
                "summary": summary,
                "target_users": target_users,
                "created_via": "mcp",
            },
        )

    @mcp.tool()
    async def apply_to_project(
        access_token: str,
        project_id: str,
        motivation: str,
        preferred_role: str = "collaborator",
    ) -> dict[str, Any]:
        """Apply to join a project as a collaborator.

        Args:
            access_token: JWT access token.
            project_id: UUID of the project to apply to.
            motivation: Brief statement of why you want to join.
            preferred_role: Preferred collaboration role.
        """
        _validate_uuid(project_id, "project_id")
        return await call_core_api(
            "POST",
            f"/api/v1/projects/{project_id}/applications",
            token=access_token,
            json_body={
                "motivation": motivation,
                "preferred_role": preferred_role,
            },
        )

    @mcp.tool()
    async def review_applicants(
        access_token: str,
        project_id: str,
    ) -> dict[str, Any]:
        """List all applicants for a project (founder only).

        Args:
            access_token: JWT access token (must be project founder).
            project_id: UUID of the project.
        """
        _validate_uuid(project_id, "project_id")
        return await call_core_api(
            "GET",
            f"/api/v1/projects/{project_id}/applications",
            token=access_token,
        )
