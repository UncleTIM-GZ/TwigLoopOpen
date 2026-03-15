"""Application review workflow — wait for founder decision with timeout."""

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from temporal.application_review.activities import (
        approve_application,
        create_application,
        expire_application,
        notify_founder,
        publish_application_event,
        reject_application,
    )
    from temporal.application_review.schemas import (
        ApplicationReviewInput,
        ApplicationReviewResult,
        ApproveApplicationInput,
        CreateApplicationInput,
        ExpireApplicationInput,
        NotifyFounderInput,
        RejectApplicationInput,
        ReviewDecision,
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
class ApplicationReviewWorkflow:
    """Submit application → notify founder → wait for decision → create seat or reject."""

    def __init__(self) -> None:
        self._decision: ReviewDecision | None = None

    @workflow.signal
    async def submit_review_decision(self, decision: ReviewDecision) -> None:
        """Signal: founder submits their review decision."""
        self._decision = decision

    @workflow.query
    def get_status(self) -> str:
        """Query: current workflow status."""
        if self._decision is None:
            return "waiting_for_review"
        return f"decided:{self._decision.decision}"

    @workflow.run
    async def run(self, input: ApplicationReviewInput) -> ApplicationReviewResult:
        # Step 1: Create application
        app_id = await workflow.execute_activity(
            create_application,
            CreateApplicationInput(
                token=input.token,
                project_id=input.project_id,
                motivation=input.motivation,
                preferred_role=input.preferred_role,
            ),
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            retry_policy=RETRY_POLICY,
        )

        # Step 2: Notify founder (best-effort)
        await workflow.execute_activity(
            notify_founder,
            NotifyFounderInput(
                project_id=input.project_id,
                application_id=app_id,
            ),
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            retry_policy=RETRY_POLICY,
        )

        # Step 3: Wait for signal (with 7-day timeout)
        try:
            await workflow.wait_condition(
                lambda: self._decision is not None,
                timeout=REVIEW_TIMEOUT,
            )
        except TimeoutError:
            # Timeout: expire the application
            await workflow.execute_activity(
                expire_application,
                ExpireApplicationInput(token=input.token, application_id=app_id),
                start_to_close_timeout=ACTIVITY_TIMEOUT,
                retry_policy=RETRY_POLICY,
            )
            await workflow.execute_activity(
                publish_application_event,
                PublishEventInput(event_type="application.expired", entity_id=app_id),
                start_to_close_timeout=ACTIVITY_TIMEOUT,
                retry_policy=RETRY_POLICY,
            )
            return ApplicationReviewResult(
                application_id=app_id, decision="expired"
            )

        decision = self._decision
        assert decision is not None  # noqa: S101

        # Step 4: Execute decision
        seat_id: str | None = None

        if decision.decision == "approved":
            seat_id = await workflow.execute_activity(
                approve_application,
                ApproveApplicationInput(
                    token=input.token,
                    application_id=app_id,
                    project_id=input.project_id,
                    actor_id=input.applicant_actor_id,
                    seat_type=decision.seat_type,
                ),
                start_to_close_timeout=ACTIVITY_TIMEOUT,
                retry_policy=RETRY_POLICY,
            )
            event_type = "application.approved"
        else:
            await workflow.execute_activity(
                reject_application,
                RejectApplicationInput(
                    token=input.token,
                    application_id=app_id,
                    reason=decision.reason,
                ),
                start_to_close_timeout=ACTIVITY_TIMEOUT,
                retry_policy=RETRY_POLICY,
            )
            event_type = "application.rejected"

        await workflow.execute_activity(
            publish_application_event,
            PublishEventInput(event_type=event_type, entity_id=app_id),
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            retry_policy=RETRY_POLICY,
        )

        return ApplicationReviewResult(
            application_id=app_id,
            decision=decision.decision,
            seat_id=seat_id,
        )
