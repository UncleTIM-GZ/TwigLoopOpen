"""MCP context tools — provide platform rules and context to AI assistants."""

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations


def _get_rules_dict() -> dict[str, Any]:
    """Return platform publish rules as a plain dict.

    Shared by the ``get_publish_rules`` tool and the
    ``twigloop://rules/publish`` MCP resource.
    """
    return {
        "quota_limits": {
            "max_work_packages_per_project": 5,
            "max_tasks_per_work_package": 6,
            "max_tasks_per_project": 20,
            "max_ewu_per_task": 8,
            "max_active_projects_new_founder": 2,
            "max_open_seats_default": 12,
            "max_active_tasks_default": 30,
            "max_pending_applications_per_project": 30,
            "max_pending_applications_per_task": 10,
        },
        "required_task_fields": [
            "title",
            "task_type",
            "goal",
            "output_spec",
            "completion_criteria",
            "main_role",
        ],
        "project_types": ["general", "public_benefit", "recruitment"],
        "founder_types": ["individual", "organization", "contributor"],
        "task_types": [
            "requirement_clarification",
            "research",
            "product_design",
            "development",
            "testing_fix",
            "documentation",
            "collaboration_support",
            "review_audit",
        ],
        "risk_levels": ["low", "medium", "high"],
        "notes": [
            "Public benefit projects require human review at key milestones.",
            "Recruitment projects have reward (has_reward=true).",
            "EWU is calculated from task_type, risk_level, and complexity factors.",
            "Always run preflight_project before publish_project_bundle.",
        ],
    }


def register_context_tools(mcp: FastMCP) -> None:
    """Register context tools on the MCP server."""

    @mcp.tool(
        title="Get Publish Rules",
        annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False),
    )
    async def get_publish_rules() -> dict[str, Any]:
        """Get all rules and constraints for publishing a project.

        Returns quota limits, required fields, and validation rules
        that an AI assistant needs to guide project creation.
        """
        return _get_rules_dict()
