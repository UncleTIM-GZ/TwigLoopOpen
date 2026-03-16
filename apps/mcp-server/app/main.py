"""Twig Loop MCP Server — standard MCP protocol implementation.

Replaces the deprecated mcp-gateway + mcp-orchestrator REST proxy architecture
with a standard MCP Server using the official `mcp` Python SDK.

Run:
    uv run python -m app.main                    # stdio transport (default)
    uv run python -m app.main --transport sse     # SSE transport
    uv run python -m app.main --transport http    # streamable HTTP transport
"""

import argparse
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from app.clients.core_api import close_client
from app.tools.auth_tools import register_auth_tools
from app.tools.context_tools import register_context_tools
from app.tools.orchestration_tools import register_orchestration_tools
from app.tools.preflight_tools import register_preflight_tools
from app.tools.project_tools import register_project_tools
from app.tools.draft_tools import register_draft_tools
from app.tools.quota_tools import register_quota_tools


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[None]:
    """Manage httpx client lifecycle — close on shutdown."""
    try:
        yield
    finally:
        await close_client()


mcp = FastMCP(
    "Twig Loop",
    instructions=(
        "Twig Loop is an AI-native project collaboration platform. "
        "Use these tools to register, authenticate, create projects, "
        "structure work packages and task cards, and apply to collaborate."
    ),
    lifespan=app_lifespan,
)

# Register all tool groups
register_auth_tools(mcp)
register_project_tools(mcp)
register_orchestration_tools(mcp)
register_quota_tools(mcp)
register_preflight_tools(mcp)
register_context_tools(mcp)
register_draft_tools(mcp)


def main() -> None:
    """Entry point for the MCP server."""
    import os

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

    # For SSE/HTTP, host and port are set via environment variables:
    #   FASTMCP_HOST (default: 127.0.0.1)
    #   FASTMCP_PORT (default: 8100)
    # Or for Railway: PORT env var is mapped to FASTMCP_PORT
    port = os.getenv("PORT", os.getenv("FASTMCP_PORT", "8100"))
    os.environ["FASTMCP_PORT"] = port
    os.environ["FASTMCP_HOST"] = os.getenv("FASTMCP_HOST", "0.0.0.0")

    mcp.run(transport=transport)  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
