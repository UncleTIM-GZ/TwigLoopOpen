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

    _register_prompts(server)
    _register_resources(server)

    return server


def _register_prompts(server: FastMCP) -> None:
    """Register MCP prompts — guided workflows for common tasks."""

    @server.prompt(
        name="create-project",
        title="Create a New Project",
        description=(
            "Guided workflow to create a structured project with work packages and task cards"
        ),
    )
    def create_project_prompt() -> str:
        return (
            "I want to create a new project on Twig Loop. "
            "Please help me define:\n"
            "1. Project type (general / public_benefit / recruitment)\n"
            "2. Title and summary\n"
            "3. Work packages with tasks\n"
            "4. Each task needs: title, task_type, goal, output_spec, "
            "completion_criteria, main_role, risk_level\n\n"
            "Use the create_project, draft_work_package, and validate_task_card tools. "
            "Run preflight_project before publishing."
        )

    @server.prompt(
        name="find-tasks",
        title="Find Tasks to Contribute",
        description="Discover open projects and tasks matching your skills",
    )
    def find_tasks_prompt() -> str:
        return (
            "I want to find tasks I can contribute to on Twig Loop. "
            "Please:\n"
            "1. Use list_projects to show open projects\n"
            "2. Help me find tasks that match my skills\n"
            "3. Use apply_to_project when I'm ready to apply\n"
            "4. Check quota limits with check_application_quota first"
        )

    @server.prompt(
        name="check-project-status",
        title="Check Project Status",
        description=(
            "Review the current state of a project including tasks, applications, and quotas"
        ),
    )
    def check_project_status_prompt() -> str:
        return (
            "I want to check the status of my project on Twig Loop. "
            "Please use get_project to show project details, "
            "review_applicants to see pending applications, "
            "and check_project_quota to verify quota usage."
        )


def _register_resources(server: FastMCP) -> None:
    """Register MCP resources — static platform data accessible by URI."""

    @server.resource(
        "twigloop://rules/publish",
        name="Publish Rules",
        description="Platform rules for project creation and publishing",
        mime_type="application/json",
    )
    def publish_rules_resource() -> str:
        import json

        from app.tools.context_tools import _get_rules_dict

        return json.dumps(_get_rules_dict())

    @server.resource(
        "twigloop://rules/quota",
        name="Quota Limits",
        description="Platform quota and complexity limits",
        mime_type="application/json",
    )
    def quota_rules_resource() -> str:
        import json

        from app.tools.context_tools import _get_rules_dict

        rules = _get_rules_dict()
        return json.dumps(rules["quota_limits"])


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

    # Set allowed hosts for remote access (Railway edge forwards with domain Host header)
    mcp.settings.transport_security.allowed_hosts = [
        "127.0.0.1:*",
        "localhost:*",
        "mcp.twigloop.tech",
        "mcp.twigloop.tech:*",
        "mcp-server-production-4ae6.up.railway.app",
        "mcp-server-production-4ae6.up.railway.app:*",
    ]

    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        import uvicorn

        host = os.getenv("FASTMCP_HOST", os.getenv("HOST", "0.0.0.0"))
        port = int(os.getenv("PORT", os.getenv("FASTMCP_PORT", "8100")))

        if transport == "streamable-http":
            app = mcp.streamable_http_app()
        else:
            app = mcp.sse_app()

        uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
