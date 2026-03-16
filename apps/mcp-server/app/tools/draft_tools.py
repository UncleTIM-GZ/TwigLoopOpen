"""MCP draft tools — create and manage drafts via core-api."""

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


def register_draft_tools(mcp: FastMCP) -> None:
    """Register draft tools on the MCP server."""

    @mcp.tool(
        title="Create Draft",
        annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=False, openWorldHint=False),
    )
    async def create_draft(
        access_token: str,
        draft_type: str,
        source_channel: str = "mcp",
        collected_fields_json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new draft to incrementally collect project or application data.

        Args:
            access_token: JWT access token.
            draft_type: Type of draft (e.g., "project", "application").
            source_channel: Channel creating this draft (default "mcp").
            collected_fields_json: Initial collected fields (optional).
        """
        body: dict[str, Any] = {
            "draft_type": draft_type,
            "source_channel": source_channel,
        }
        if collected_fields_json:
            body["collected_fields_json"] = collected_fields_json
        return await call_core_api("POST", "/api/v1/drafts/", token=access_token, json_body=body)

    @mcp.tool(
        title="Update Draft",
        annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=True, openWorldHint=False),
    )
    async def update_draft(
        access_token: str,
        draft_id: str,
        collected_fields_json: dict[str, Any] | None = None,
        missing_fields_json: list[Any] | None = None,
        warnings_json: list[Any] | None = None,
        last_llm_summary: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing draft with new collected fields or metadata.

        Args:
            access_token: JWT access token.
            draft_id: UUID of the draft to update.
            collected_fields_json: Updated collected fields (optional).
            missing_fields_json: Updated missing fields list (optional).
            warnings_json: Updated warnings list (optional).
            last_llm_summary: Updated LLM summary text (optional).
        """
        _validate_uuid(draft_id, "draft_id")
        body: dict[str, Any] = {}
        if collected_fields_json is not None:
            body["collected_fields_json"] = collected_fields_json
        if missing_fields_json is not None:
            body["missing_fields_json"] = missing_fields_json
        if warnings_json is not None:
            body["warnings_json"] = warnings_json
        if last_llm_summary is not None:
            body["last_llm_summary"] = last_llm_summary
        return await call_core_api(
            "PATCH",
            f"/api/v1/drafts/{draft_id}",
            token=access_token,
            json_body=body,
        )

    @mcp.tool(
        title="Get Draft",
        annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False),
    )
    async def get_draft(
        access_token: str,
        draft_id: str,
    ) -> dict[str, Any]:
        """Get a single draft by ID.

        Args:
            access_token: JWT access token.
            draft_id: UUID of the draft.
        """
        _validate_uuid(draft_id, "draft_id")
        return await call_core_api(
            "GET",
            f"/api/v1/drafts/{draft_id}",
            token=access_token,
        )

    @mcp.tool(
        title="List My Drafts",
        annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False),
    )
    async def list_my_drafts(
        access_token: str,
    ) -> dict[str, Any]:
        """List all drafts belonging to the current actor.

        Args:
            access_token: JWT access token.
        """
        return await call_core_api("GET", "/api/v1/drafts/", token=access_token)

    @mcp.tool(
        title="Delete Draft",
        annotations=ToolAnnotations(
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def delete_draft(
        access_token: str,
        draft_id: str,
    ) -> dict[str, Any]:
        """Delete a draft by ID.

        Args:
            access_token: JWT access token.
            draft_id: UUID of the draft to delete.
        """
        _validate_uuid(draft_id, "draft_id")
        return await call_core_api(
            "DELETE",
            f"/api/v1/drafts/{draft_id}",
            token=access_token,
        )
