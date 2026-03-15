"""Workflow starter — facade functions to start Temporal workflows from external services."""

import uuid
from typing import Any

from shared_config import TemporalSettings

from temporal.application_review.schemas import ApplicationReviewInput
from temporal.application_review.workflows import ApplicationReviewWorkflow
from temporal.client import get_temporal_client
from temporal.project_publish.schemas import (
    PublishProjectInput,
    PublishProjectResult,
    TaskInput,
    WorkPackageInput,
)
from temporal.project_publish.workflows import PublishProjectWorkflow
from temporal.public_benefit_review.schemas import PublicBenefitReviewInput
from temporal.public_benefit_review.workflows import PublicBenefitReviewWorkflow

_settings = TemporalSettings()


async def start_publish_project(
    token: str,
    project_type: str,
    founder_type: str,
    title: str,
    summary: str,
    work_packages: list[dict[str, Any]],
    target_users: str | None = None,
) -> PublishProjectResult:
    """Start a project publish workflow and wait for completion."""
    client = await get_temporal_client()

    wf_input = PublishProjectInput(
        token=token,
        project_type=project_type,
        founder_type=founder_type,
        title=title,
        summary=summary,
        target_users=target_users,
        work_packages=[
            WorkPackageInput(
                title=wp["title"],
                description=wp.get("description"),
                tasks=[
                    TaskInput(**task)
                    for task in wp.get("tasks", [])
                ],
            )
            for wp in work_packages
        ],
    )

    return await client.execute_workflow(
        PublishProjectWorkflow.run,
        wf_input,
        id=f"publish-project-{uuid.uuid4().hex[:8]}",
        task_queue=_settings.temporal_task_queue,
    )


async def start_application_review(
    token: str,
    project_id: str,
    applicant_actor_id: str,
    motivation: str,
    preferred_role: str = "collaborator",
) -> str:
    """Start an application review workflow. Returns workflow run ID."""
    client = await get_temporal_client()

    wf_input = ApplicationReviewInput(
        token=token,
        project_id=project_id,
        applicant_actor_id=applicant_actor_id,
        motivation=motivation,
        preferred_role=preferred_role,
    )

    wf_id = f"app-review-{project_id[:8]}-{uuid.uuid4().hex[:8]}"
    handle = await client.start_workflow(
        ApplicationReviewWorkflow.run,
        wf_input,
        id=wf_id,
        task_queue=_settings.temporal_task_queue,
    )
    return handle.id


async def start_public_benefit_review(
    token: str,
    project_id: str,
    milestone: str,
    reviewer_id: str,
) -> str:
    """Start a public benefit review workflow. Returns workflow run ID."""
    client = await get_temporal_client()

    wf_input = PublicBenefitReviewInput(
        token=token,
        project_id=project_id,
        milestone=milestone,
        reviewer_id=reviewer_id,
    )

    wf_id = f"pb-review-{project_id[:8]}-{uuid.uuid4().hex[:8]}"
    handle = await client.start_workflow(
        PublicBenefitReviewWorkflow.run,
        wf_input,
        id=wf_id,
        task_queue=_settings.temporal_task_queue,
    )
    return handle.id
