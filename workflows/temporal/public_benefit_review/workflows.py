"""Public benefit review workflow — enforce human review at key milestones."""

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from temporal.public_benefit_review.activities import (
        mark_review_required,
        notify_reviewer,
        publish_review_event,
        reject_project,
        request_revision,
        update_project_review_passed,
    )
    from temporal.public_benefit_review.schemas import (
        MarkReviewRequiredInput,
        NotifyReviewerInput,
        PublicBenefitReviewInput,
        PublicBenefitReviewOutput,
        RejectProjectInput,
        RequestRevisionInput,
        ReviewResult,
        UpdateProjectReviewPassedInput,
    )
    from temporal.shared_schemas import PublishEventInput

ACTIVITY_TIMEOUT = timedelta(seconds=30)
RETRY_POLICY = RetryPolicy(
    maximum_attempts=3,
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
)
REVIEW_TIMEOUT = timedelta(days=7)


@workflow.defn
class PublicBenefitReviewWorkflow:
    """Mark milestone → notify reviewer → wait for decision → update status."""

    def __init__(self) -> None:
        self._result: ReviewResult | None = None

    @workflow.signal
    async def submit_review_result(self, result: ReviewResult) -> None:
        """Signal: reviewer submits their decision."""
        self._result = result

    @workflow.query
    def get_status(self) -> str:
        """Query: current workflow status."""
        if self._result is None:
            return "waiting_for_review"
        return f"decided:{self._result.decision}"

    @workflow.run
    async def run(
        self, input: PublicBenefitReviewInput
    ) -> PublicBenefitReviewOutput:
        # Step 1: Mark as requiring review
        await workflow.execute_activity(
            mark_review_required,
            MarkReviewRequiredInput(
                token=input.token,
                project_id=input.project_id,
                milestone=input.milestone,
            ),
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            retry_policy=RETRY_POLICY,
        )

        # Step 2: Notify reviewer (best-effort)
        await workflow.execute_activity(
            notify_reviewer,
            NotifyReviewerInput(
                project_id=input.project_id,
                reviewer_id=input.reviewer_id,
                milestone=input.milestone,
            ),
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            retry_policy=RETRY_POLICY,
        )

        # Step 3: Wait for signal (7-day timeout)
        try:
            await workflow.wait_condition(
                lambda: self._result is not None,
                timeout=REVIEW_TIMEOUT,
            )
        except TimeoutError:
            await workflow.execute_activity(
                publish_review_event,
                PublishEventInput(
                    event_type="review.expired",
                    entity_id=input.project_id,
                ),
                start_to_close_timeout=ACTIVITY_TIMEOUT,
                retry_policy=RETRY_POLICY,
            )
            return PublicBenefitReviewOutput(
                project_id=input.project_id,
                milestone=input.milestone,
                decision="expired",
            )

        result = self._result
        assert result is not None  # noqa: S101

        # Step 4: Execute decision
        if result.decision == "passed":
            await workflow.execute_activity(
                update_project_review_passed,
                UpdateProjectReviewPassedInput(
                    token=input.token,
                    project_id=input.project_id,
                ),
                start_to_close_timeout=ACTIVITY_TIMEOUT,
                retry_policy=RETRY_POLICY,
            )
        elif result.decision == "needs_revision":
            await workflow.execute_activity(
                request_revision,
                RequestRevisionInput(
                    token=input.token,
                    project_id=input.project_id,
                    feedback=result.feedback,
                ),
                start_to_close_timeout=ACTIVITY_TIMEOUT,
                retry_policy=RETRY_POLICY,
            )
        else:
            await workflow.execute_activity(
                reject_project,
                RejectProjectInput(
                    token=input.token,
                    project_id=input.project_id,
                    reason=result.feedback,
                ),
                start_to_close_timeout=ACTIVITY_TIMEOUT,
                retry_policy=RETRY_POLICY,
            )

        await workflow.execute_activity(
            publish_review_event,
            PublishEventInput(
                event_type=f"review.{result.decision}",
                entity_id=input.project_id,
            ),
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            retry_policy=RETRY_POLICY,
        )

        return PublicBenefitReviewOutput(
            project_id=input.project_id,
            milestone=input.milestone,
            decision=result.decision,
        )
