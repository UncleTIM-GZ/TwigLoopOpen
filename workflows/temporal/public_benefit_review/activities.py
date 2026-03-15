"""Activities for the public benefit review workflow."""

from temporalio import activity

from temporal.core_api import call_core_api
from temporal.public_benefit_review.schemas import (
    MarkReviewRequiredInput,
    NotifyReviewerInput,
    RejectProjectInput,
    RequestRevisionInput,
    UpdateProjectReviewPassedInput,
)
from temporal.shared_schemas import PublishEventInput


@activity.defn
async def mark_review_required(input: MarkReviewRequiredInput) -> None:
    """Mark a project milestone as requiring human review."""
    await call_core_api(
        "PATCH",
        f"/api/v1/projects/{input.project_id}/status",
        token=input.token,
        json_body={"status": "reviewer_required", "milestone": input.milestone},
    )


@activity.defn
async def notify_reviewer(input: NotifyReviewerInput) -> None:
    """Notify the assigned reviewer about a pending review."""
    try:
        await call_core_api(
            "POST",
            "/api/v1/notifications/send",
            json_body={
                "type": "review_required",
                "project_id": input.project_id,
                "reviewer_id": input.reviewer_id,
                "milestone": input.milestone,
            },
        )
    except RuntimeError:
        activity.logger.warning(
            "Failed to notify reviewer %s for project %s",
            input.reviewer_id,
            input.project_id,
        )


@activity.defn
async def update_project_review_passed(
    input: UpdateProjectReviewPassedInput,
) -> None:
    """Update project status to human_review_passed."""
    await call_core_api(
        "PATCH",
        f"/api/v1/projects/{input.project_id}/status",
        token=input.token,
        json_body={"status": "human_review_passed"},
    )


@activity.defn
async def request_revision(input: RequestRevisionInput) -> None:
    """Request revision on a project after review."""
    await call_core_api(
        "PATCH",
        f"/api/v1/projects/{input.project_id}/status",
        token=input.token,
        json_body={"status": "revision_requested", "feedback": input.feedback},
    )


@activity.defn
async def reject_project(input: RejectProjectInput) -> None:
    """Reject a public benefit project."""
    await call_core_api(
        "PATCH",
        f"/api/v1/projects/{input.project_id}/status",
        token=input.token,
        json_body={"status": "rejected", "reason": input.reason},
    )


@activity.defn
async def publish_review_event(input: PublishEventInput) -> None:
    """Publish a NATS event for review status change."""
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
