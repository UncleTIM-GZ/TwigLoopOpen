"""Project publish workflow — durable multi-step project creation."""

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from temporal.project_publish.activities import (
        create_project,
        create_task_card,
        create_work_package,
        mark_project_draft,
        publish_project_event,
    )
    from temporal.project_publish.schemas import (
        CreateProjectInput,
        CreateTaskCardInput,
        CreateWorkPackageInput,
        MarkProjectDraftInput,
        PublishEventInput,
        PublishProjectInput,
        PublishProjectResult,
    )

ACTIVITY_TIMEOUT = timedelta(seconds=30)
RETRY_POLICY = RetryPolicy(
    maximum_attempts=3,
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
)


@workflow.defn
class PublishProjectWorkflow:
    """Orchestrate project creation → work packages → task cards → event."""

    @workflow.run
    async def run(self, input: PublishProjectInput) -> PublishProjectResult:
        # Step 1: Create project
        project_id = await workflow.execute_activity(
            create_project,
            CreateProjectInput(
                token=input.token,
                project_type=input.project_type,
                founder_type=input.founder_type,
                title=input.title,
                summary=input.summary,
                target_users=input.target_users,
            ),
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            retry_policy=RETRY_POLICY,
        )

        wp_ids: list[str] = []
        task_ids: list[str] = []

        try:
            # Step 2: Create work packages + tasks
            for i, wp in enumerate(input.work_packages):
                wp_id = await workflow.execute_activity(
                    create_work_package,
                    CreateWorkPackageInput(
                        token=input.token,
                        project_id=project_id,
                        title=wp.title,
                        description=wp.description,
                        sort_order=i,
                    ),
                    start_to_close_timeout=ACTIVITY_TIMEOUT,
                    retry_policy=RETRY_POLICY,
                )
                wp_ids.append(wp_id)

                for task in wp.tasks:
                    task_id = await workflow.execute_activity(
                        create_task_card,
                        CreateTaskCardInput(
                            token=input.token,
                            work_package_id=wp_id,
                            title=task.title,
                            task_type=task.task_type,
                            goal=task.goal,
                            output_spec=task.output_spec,
                            completion_criteria=task.completion_criteria,
                            main_role=task.main_role,
                            risk_level=task.risk_level,
                            ewu=task.ewu,
                        ),
                        start_to_close_timeout=ACTIVITY_TIMEOUT,
                        retry_policy=RETRY_POLICY,
                    )
                    task_ids.append(task_id)

        except Exception:
            # Compensation: mark project as draft so user can retry
            await workflow.execute_activity(
                mark_project_draft,
                MarkProjectDraftInput(token=input.token, project_id=project_id),
                start_to_close_timeout=ACTIVITY_TIMEOUT,
            )
            raise

        # Step 3: Publish event (best-effort)
        await workflow.execute_activity(
            publish_project_event,
            PublishEventInput(
                event_type="project.published",
                entity_id=project_id,
            ),
            start_to_close_timeout=ACTIVITY_TIMEOUT,
        )

        return PublishProjectResult(
            project_id=project_id,
            work_package_ids=wp_ids,
            task_ids=task_ids,
        )
