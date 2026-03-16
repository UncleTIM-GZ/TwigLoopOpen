"""Activities for the application review workflow."""

from temporalio import activity

from temporal.application_review.schemas import (
    ApproveApplicationInput,
    CreateApplicationInput,
    ExpireApplicationInput,
    NotifyFounderInput,
    RejectApplicationInput,
)
from temporal.core_api import call_core_api
from temporal.shared_schemas import PublishEventInput


@activity.defn
async def create_application(input: CreateApplicationInput) -> str:
    """Create an application via core-api. Returns application_id."""
    data = await call_core_api(
        "POST",
        f"/api/v1/projects/{input.project_id}/applications",
        token=input.token,
        json_body={
            "motivation": input.motivation,
            "preferred_role": input.preferred_role,
        },
    )
    result: str = data["data"]["application_id"]
    return result


@activity.defn
async def notify_founder(input: NotifyFounderInput) -> None:
    """Notify the project founder about a new application."""
    try:
        await call_core_api(
            "POST",
            "/api/v1/notifications/send",
            json_body={
                "type": "new_application",
                "project_id": input.project_id,
                "application_id": input.application_id,
            },
        )
    except RuntimeError:
        activity.logger.warning(
            "Failed to notify founder for application %s", input.application_id
        )


@activity.defn
async def approve_application(input: ApproveApplicationInput) -> str:
    """Approve application and create a project seat. Returns seat_id."""
    # Approve the application
    await call_core_api(
        "PATCH",
        f"/api/v1/applications/{input.application_id}",
        token=input.token,
        json_body={"status": "approved"},
    )
    # Create seat
    data = await call_core_api(
        "POST",
        f"/api/v1/projects/{input.project_id}/seats",
        token=input.token,
        json_body={
            "actor_id": input.actor_id,
            "seat_type": input.seat_type,
        },
    )
    result: str = data["data"]["seat_id"]
    return result


@activity.defn
async def reject_application(input: RejectApplicationInput) -> None:
    """Reject an application."""
    await call_core_api(
        "PATCH",
        f"/api/v1/applications/{input.application_id}",
        token=input.token,
        json_body={"status": "rejected", "reason": input.reason},
    )


@activity.defn
async def expire_application(input: ExpireApplicationInput) -> None:
    """Mark an application as expired (review timeout)."""
    await call_core_api(
        "PATCH",
        f"/api/v1/applications/{input.application_id}",
        token=input.token,
        json_body={"status": "expired"},
    )


@activity.defn
async def publish_application_event(input: PublishEventInput) -> None:
    """Publish a NATS event for application status change."""
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
