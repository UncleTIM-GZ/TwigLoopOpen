"""Temporal Worker — runs all Twig Loop workflows.

Usage:
    uv run python -m temporal.worker
"""

import asyncio

from shared_config import TemporalSettings
from temporalio.worker import Worker

from temporal.application_review.activities import (
    approve_application,
    create_application,
    expire_application,
    notify_founder,
    publish_application_event,
    reject_application,
)
from temporal.application_review.workflows import ApplicationReviewWorkflow
from temporal.client import get_temporal_client
from temporal.project_publish.activities import (
    create_project,
    create_task_card,
    create_work_package,
    mark_project_draft,
    publish_project_event,
)
from temporal.project_publish.workflows import PublishProjectWorkflow
from temporal.public_benefit_review.activities import (
    mark_review_required,
    notify_reviewer,
    publish_review_event,
    reject_project,
    request_revision,
    update_project_review_passed,
)
from temporal.public_benefit_review.workflows import PublicBenefitReviewWorkflow

_settings = TemporalSettings()


async def run_worker() -> None:
    """Start the Temporal worker with all workflows and activities."""
    client = await get_temporal_client()

    worker = Worker(
        client,
        task_queue=_settings.temporal_task_queue,
        workflows=[
            PublishProjectWorkflow,
            ApplicationReviewWorkflow,
            PublicBenefitReviewWorkflow,
        ],
        activities=[
            # project_publish
            create_project,
            create_work_package,
            create_task_card,
            publish_project_event,
            mark_project_draft,
            # application_review
            create_application,
            notify_founder,
            approve_application,
            reject_application,
            expire_application,
            publish_application_event,
            # public_benefit_review
            mark_review_required,
            notify_reviewer,
            update_project_review_passed,
            request_revision,
            reject_project,
            publish_review_event,
        ],
    )

    print(f"Worker started on queue '{_settings.temporal_task_queue}'")  # noqa: T201
    await worker.run()


def main() -> None:
    """Entry point."""
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
