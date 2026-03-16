"""NATS JetStream subject constants.

Naming convention: domain.entity.action
"""


class Subjects:
    """Event subject name constants."""

    # Account events
    ACCOUNT_REGISTERED = "account.account.registered"

    # Project events
    PROJECT_CREATED = "project.project.created"
    PROJECT_PUBLISHED = "project.project.published"
    PROJECT_ARCHIVED = "project.project.archived"

    # Application events
    APPLICATION_SUBMITTED = "project.application.submitted"
    APPLICATION_ACCEPTED = "project.application.accepted"
    APPLICATION_REJECTED = "project.application.rejected"
    APPLICATION_WITHDRAWN = "project.application.withdrawn"

    # Task events
    TASK_CREATED = "project.task.created"
    TASK_STARTED = "project.task.started"
    TASK_COMPLETED = "project.task.completed"

    # Review events
    REVIEW_REQUESTED = "review.review.requested"
    REVIEW_SUBMITTED = "review.review.submitted"

    # Sponsor events
    SPONSOR_SUPPORT_CREATED = "sponsor.support.created"

    # Credential events
    CREDENTIAL_ISSUED = "credential.credential.issued"

    # Source events
    SOURCE_WEBHOOK_RECEIVED = "source.webhook.received"
    SOURCE_SIGNAL_RECEIVED = "source.signal.received"
    SOURCE_BOUND = "source.source.bound"
    SOURCE_UNBOUND = "source.source.unbound"
