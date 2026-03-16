"""MCP quota tools — platform quota rules and preflight checks."""

import re
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from app.clients.core_api import call_core_api

_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)


def _validate_uuid(value: str, name: str) -> None:
    """Raise ValueError if value is not a valid UUID."""
    if not _UUID_RE.match(value):
        raise ValueError(f"Invalid {name}: must be a UUID (got '{value}')")


def register_quota_tools(mcp: FastMCP) -> None:
    """Register quota tools on the MCP server."""

    @mcp.tool(
        title="Get Quota Rules",
        annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False),
    )
    async def get_quota_rules() -> dict[str, Any]:
        """Get platform quota rules and their current limits.

        Returns all object volume limits, founder concurrency limits,
        and relationship limits.
        """
        return await call_core_api("GET", "/api/v1/quotas/rules")

    @mcp.tool(
        title="Check Project Quota",
        annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False),
    )
    async def check_project_quota(
        access_token: str,
        work_packages: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Check if project data passes all quota rules.

        Args:
            access_token: JWT access token.
            work_packages: List of work packages with nested tasks.
        """
        return await call_core_api(
            "POST",
            "/api/v1/quotas/check-project",
            token=access_token,
            json_body={"work_packages": work_packages or []},
        )

    @mcp.tool(
        title="Check Application Quota",
        annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False),
    )
    async def check_application_quota(
        access_token: str,
        project_id: str,
        task_id: str | None = None,
    ) -> dict[str, Any]:
        """Check if application passes quota rules.

        Args:
            access_token: JWT access token.
            project_id: UUID of the project.
            task_id: Optional UUID of the specific task.
        """
        _validate_uuid(project_id, "project_id")
        body: dict[str, Any] = {"project_id": project_id}
        if task_id is not None:
            _validate_uuid(task_id, "task_id")
            body["task_id"] = task_id
        return await call_core_api(
            "POST",
            "/api/v1/quotas/check-application",
            token=access_token,
            json_body=body,
        )
