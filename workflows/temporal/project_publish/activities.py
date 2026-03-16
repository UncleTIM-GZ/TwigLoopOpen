"""Activities for the project publish workflow."""

from temporalio import activity

from temporal.core_api import call_core_api
from temporal.project_publish.schemas import (
    CreateProjectInput,
    CreateTaskCardInput,
    CreateWorkPackageInput,
    MarkProjectDraftInput,
    PublishEventInput,
)


@activity.defn
async def create_project(input: CreateProjectInput) -> str:
    """Create a project via core-api. Returns project_id."""
    data = await call_core_api(
        "POST",
        "/api/v1/projects/",
        token=input.token,
        json_body={
            "project_type": input.project_type,
            "founder_type": input.founder_type,
            "title": input.title,
            "summary": input.summary,
            "target_users": input.target_users,
            "created_via": "mcp",
        },
    )
    result: str = data["data"]["project_id"]
    return result


@activity.defn
async def create_work_package(input: CreateWorkPackageInput) -> str:
    """Create a work package via core-api. Returns work_package_id."""
    data = await call_core_api(
        "POST",
        f"/api/v1/projects/{input.project_id}/work-packages",
        token=input.token,
        json_body={
            "title": input.title,
            "description": input.description,
            "sort_order": input.sort_order,
        },
    )
    result: str = data["data"]["work_package_id"]
    return result


@activity.defn
async def create_task_card(input: CreateTaskCardInput) -> str:
    """Create a task card via core-api. Returns task_id."""
    data = await call_core_api(
        "POST",
        f"/api/v1/work-packages/{input.work_package_id}/tasks",
        token=input.token,
        json_body={
            "title": input.title,
            "task_type": input.task_type,
            "goal": input.goal,
            "output_spec": input.output_spec,
            "completion_criteria": input.completion_criteria,
            "main_role": input.main_role,
            "risk_level": input.risk_level,
            "ewu": input.ewu,
        },
    )
    result: str = data["data"]["task_id"]
    return result


@activity.defn
async def mark_project_draft(input: MarkProjectDraftInput) -> None:
    """Mark project as draft (compensation on failure)."""
    await call_core_api(
        "PATCH",
        f"/api/v1/projects/{input.project_id}/status",
        token=input.token,
        json_body={"status": "draft"},
    )


@activity.defn
async def publish_project_event(input: PublishEventInput) -> None:
    """Publish a NATS event for the project. Best-effort, does not fail workflow."""
    try:
        await call_core_api(
            "POST",
            "/api/v1/events/publish",
            json_body={
                "event_type": input.event_type,
                "entity_id": input.entity_id,
            },
        )
    except RuntimeError:
        activity.logger.warning(
            "Failed to publish event %s for %s", input.event_type, input.entity_id
        )
