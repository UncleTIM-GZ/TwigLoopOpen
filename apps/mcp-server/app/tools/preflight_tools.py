"""MCP preflight tools — combined validation before project publish."""

import json
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from app.clients.core_api import call_core_api


def register_preflight_tools(mcp: FastMCP) -> None:
    """Register preflight tools on the MCP server."""

    @mcp.tool(
        title="Preflight Project",
        annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False),
    )
    async def preflight_project(
        access_token: str,
        collected_fields_json: str,
    ) -> dict[str, Any]:
        """Run all preflight checks before publishing a project.

        Combines task card validation and quota checks into a single call.

        Args:
            access_token: JWT access token.
            collected_fields_json: JSON string with full project structure,
                e.g. {"work_packages": [{"title": "...", "tasks": [...]}]}.
        """
        fields = json.loads(collected_fields_json)
        all_violations: list[dict[str, Any]] = []

        # 1. Validate each task card's required fields
        for wp in fields.get("work_packages", []):
            for task in wp.get("tasks", []):
                errors: list[str] = []
                if not task.get("title", "").strip():
                    errors.append("Title is required")
                if not task.get("goal", "").strip():
                    errors.append("Goal is required")
                if not task.get("output_spec", "").strip():
                    errors.append("Output spec is required")
                if not task.get("completion_criteria", "").strip():
                    errors.append("Completion criteria is required")
                if not task.get("main_role", "").strip():
                    errors.append("Main role is required")
                for err in errors:
                    all_violations.append(
                        {
                            "rule_code": "TASK_FIELD_MISSING",
                            "severity": "error",
                            "object_scope": f"task:{task.get('title', '?')}",
                            "current_value": 0,
                            "max_allowed": 0,
                            "message": err,
                            "recommended_next_action": "Fill in the missing field",
                        }
                    )

        # 2. Run quota checks via core-api
        try:
            quota_result = await call_core_api(
                "POST",
                "/api/v1/quotas/check-project",
                token=access_token,
                json_body=fields,
            )
            quota_violations = quota_result.get("data", {}).get("violations", [])
            all_violations.extend(quota_violations)
        except RuntimeError as err:
            all_violations.append(
                {
                    "rule_code": "QUOTA_CHECK_FAILED",
                    "severity": "warning",
                    "object_scope": "system",
                    "current_value": 0,
                    "max_allowed": 0,
                    "message": f"Quota check unavailable: {err}",
                    "recommended_next_action": "Retry or proceed with caution",
                }
            )

        error_count = sum(1 for v in all_violations if v.get("severity") == "error")

        return {
            "passed": error_count == 0,
            "violations": all_violations,
            "error_count": error_count,
            "warning_count": len(all_violations) - error_count,
        }
