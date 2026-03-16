"""Twig Loop MCP Server — standard MCP protocol implementation.

Run:
    uv run python -m app.main                    # stdio transport (default)
    uv run python -m app.main --transport sse     # SSE transport
    uv run python -m app.main --transport http    # streamable HTTP transport

Environment variables for SSE/HTTP:
    FASTMCP_HOST (default: 0.0.0.0)
    FASTMCP_PORT (default: 8100, or Railway's PORT)
    CORE_API_BASE_URL (default: http://localhost:8000)
"""

import argparse
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from app.clients.core_api import close_client
from app.tools.auth_tools import register_auth_tools
from app.tools.context_tools import register_context_tools
from app.tools.draft_tools import register_draft_tools
from app.tools.orchestration_tools import register_orchestration_tools
from app.tools.preflight_tools import register_preflight_tools
from app.tools.project_tools import register_project_tools
from app.tools.quota_tools import register_quota_tools


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[None]:
    """Manage httpx client lifecycle — close on shutdown."""
    try:
        yield
    finally:
        await close_client()


def create_mcp() -> FastMCP:
    """Create and configure FastMCP instance.

    Must be called after environment variables are set so FastMCP Settings
    picks up FASTMCP_HOST and FASTMCP_PORT correctly.
    """
    server = FastMCP(
        "Twig Loop",
        instructions=(
            "Twig Loop is an AI-native project collaboration platform. "
            "Use these tools to register, authenticate, create projects, "
            "structure work packages and task cards, and apply to collaborate."
        ),
        lifespan=app_lifespan,
    )

    register_auth_tools(server)
    register_project_tools(server)
    register_orchestration_tools(server)
    register_quota_tools(server)
    register_preflight_tools(server)
    register_context_tools(server)
    register_draft_tools(server)

    return server


def main() -> None:
    """Entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="Twig Loop MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http"],
        default=os.getenv("MCP_TRANSPORT", "stdio"),
        help="MCP transport protocol (default: stdio, env: MCP_TRANSPORT)",
    )
    args = parser.parse_args()

    transport = args.transport
    if transport == "http":
        transport = "streamable-http"

    # Ensure FASTMCP_HOST/PORT are set BEFORE creating FastMCP
    if "FASTMCP_PORT" not in os.environ:
        os.environ["FASTMCP_PORT"] = os.getenv("PORT", "8100")
    if "FASTMCP_HOST" not in os.environ:
        os.environ["FASTMCP_HOST"] = "0.0.0.0"

    mcp = create_mcp()
    mcp.run(transport=transport)  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
