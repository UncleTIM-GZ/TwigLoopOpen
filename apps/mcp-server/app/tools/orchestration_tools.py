"""MCP orchestration tools — multi-step project publish workflow."""

import os
import re
from typing import Any

from mcp.server.fastmcp import FastMCP

from app.clients.core_api import call_core_api

USE_TEMPORAL = os.getenv("USE_TEMPORAL_WORKFLOWS", "false").lower() == "true"

_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)


def _validate_uuid(value: str, name: str) -> None:
    """Raise ValueError if value is not a valid UUID."""
    if not _UUID_RE.match(value):
        raise ValueError(f"Invalid {name}: must be a UUID (got '{value}')")


def register_orchestration_tools(mcp: FastMCP) -> None:
    """Register orchestration tools on the MCP server."""

    @mcp.tool()
    async def publish_project_bundle(
        access_token: str,
        project_type: str,
        founder_type: str,
        title: str,
        summary: str,
        work_packages: list[dict[str, Any]],
        target_users: str | None = None,
    ) -> dict[str, Any]:
        """Publish a complete project with work packages and tasks in one step.

        This orchestrates: project creation → work package creation → task card
        creation → EWU calculation. Replaces the old MCP Orchestrator REST endpoint.

        Args:
            access_token: JWT access token.
            project_type: One of "general", "public_benefit", "recruitment".
            founder_type: One of "individual", "organization", "contributor".
            title: Project title.
            summary: Brief description of the project.
            work_packages: List of work packages, each with "title", optional
                "description", and "tasks" list. Each task has "title", "task_type",
                "goal", "output_spec", "completion_criteria", "main_role",
                optional "risk_level" (default "low"), optional "ewu" (default 1.0).
            target_users: Who this project serves (optional).
        """
        # Route through Temporal if configured
        if USE_TEMPORAL:
            from temporal.starter import start_publish_project

            wf_result = await start_publish_project(
                token=access_token,
                project_type=project_type,
                founder_type=founder_type,
                title=title,
                summary=summary,
                work_packages=work_packages,
                target_users=target_users,
            )
            return {
                "project_id": wf_result.project_id,
                "work_package_ids": wf_result.work_package_ids,
                "task_ids": wf_result.task_ids,
                "via": "temporal",
            }

        # Direct HTTP path (default)
        # Step 1: Create project
        project_res = await call_core_api(
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
        project_id = project_res["data"]["project_id"]

        # Step 2: Create work packages + tasks (with partial result on failure)
        wp_ids: list[str] = []
        task_ids: list[str] = []
        errors: list[str] = []

        for i, wp_input in enumerate(work_packages):
            try:
                wp_res = await call_core_api(
                    "POST",
                    f"/api/v1/projects/{project_id}/work-packages",
                    token=access_token,
                    json_body={
                        "title": wp_input["title"],
                        "description": wp_input.get("description"),
                        "sort_order": i,
                    },
                )
            except RuntimeError as err:
                errors.append(f"Work package '{wp_input.get('title', i)}': {err}")
                continue

            wp_id = wp_res["data"]["work_package_id"]
            wp_ids.append(wp_id)

            for task_input in wp_input.get("tasks", []):
                try:
                    task_res = await call_core_api(
                        "POST",
                        f"/api/v1/work-packages/{wp_id}/tasks",
                        token=access_token,
                        json_body=task_input,
                    )
                    task_ids.append(task_res["data"]["task_id"])
                except RuntimeError as err:
                    task_title = task_input.get("title", "?")
                    wp_title = wp_input.get("title", str(i))
                    errors.append(f"Task '{task_title}' in WP '{wp_title}': {err}")

        result: dict[str, Any] = {
            "project_id": project_id,
            "work_package_ids": wp_ids,
            "task_ids": task_ids,
        }
        if errors:
            result["partial"] = True
            result["errors"] = errors

        return result

    @mcp.tool()
    async def draft_work_package(
        access_token: str,
        project_id: str,
        title: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create a draft work package for a project.

        Args:
            access_token: JWT access token.
            project_id: UUID of the project.
            title: Work package title.
            description: Optional detailed description.
        """
        _validate_uuid(project_id, "project_id")
        return await call_core_api(
            "POST",
            f"/api/v1/projects/{project_id}/work-packages",
            token=access_token,
            json_body={"title": title, "description": description},
        )

    @mcp.tool()
    async def validate_task_card(
        title: str,
        goal: str,
        output_spec: str,
        completion_criteria: str,
        main_role: str,
    ) -> dict[str, Any]:
        """Validate a task card meets minimum quality requirements.

        Checks: single output spec, single main role, completion criteria present.

        Args:
            title: Task title.
            goal: Task goal description.
            output_spec: Primary deliverable.
            completion_criteria: How to determine task is done.
            main_role: Primary responsible role.
        """
        errors: list[str] = []
        if not title.strip():
            errors.append("Title is required")
        if not goal.strip():
            errors.append("Goal is required")
        if not output_spec.strip():
            errors.append("Output spec is required")
        if not completion_criteria.strip():
            errors.append("Completion criteria is required")
        if not main_role.strip():
            errors.append("Main role is required")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "task_preview": {
                "title": title,
                "goal": goal,
                "output_spec": output_spec,
                "completion_criteria": completion_criteria,
                "main_role": main_role,
            },
        }

    # calculate_ewu tool REMOVED (2026-03-15, P0 hardening).
    # EWU calculation is owned solely by core-api (app/domain/ewu.py).
    # MCP consumers should pass ewu values via publish_project_bundle
    # or let core-api compute them at task creation time.
