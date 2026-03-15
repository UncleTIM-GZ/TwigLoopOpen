"""All domain enums for Twig Loop, derived from .docs/ Schema."""

from enum import StrEnum


class RegistrationSource(StrEnum):
    WEB = "web"
    MCP = "mcp"
    OAUTH = "oauth"


class AccountStatus(StrEnum):
    ACTIVE = "active"
    PENDING_VERIFICATION = "pending_verification"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class ActorType(StrEnum):
    HUMAN = "human"
    AGENT = "agent"
    OPERATOR = "operator"


class ActorProfileStatus(StrEnum):
    ACTIVE = "active"
    PROFILE_INCOMPLETE = "profile_incomplete"
    RESTRICTED = "restricted"
    ARCHIVED = "archived"


class ActorLevel(StrEnum):
    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"


class FounderType(StrEnum):
    ORDINARY = "ordinary"
    HELP_SEEKER = "help_seeker"
    CONTRIBUTOR = "contributor"


class ProjectType(StrEnum):
    GENERAL = "general"
    PUBLIC_BENEFIT = "public_benefit"
    RECRUITMENT = "recruitment"


class ProjectStatus(StrEnum):
    DRAFT = "draft"
    OPEN_FOR_COLLABORATION = "open_for_collaboration"
    TEAM_FORMING = "team_forming"
    REVIEWER_REQUIRED = "reviewer_required"
    IN_PROGRESS = "in_progress"
    READY_FOR_MILESTONE_CHECK = "ready_for_milestone_check"
    HUMAN_REVIEW_PASSED = "human_review_passed"
    DELIVERED = "delivered"
    PAUSED = "paused"
    CLOSED = "closed"


class WorkPackageStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    BLOCKED = "blocked"
    READY_FOR_COMPLETION = "ready_for_completion"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TaskType(StrEnum):
    REQUIREMENT_CLARIFICATION = "requirement_clarification"
    RESEARCH = "research"
    PRODUCT_DESIGN = "product_design"
    DEVELOPMENT = "development"
    TESTING_FIX = "testing_fix"
    DOCUMENTATION = "documentation"
    COLLABORATION_SUPPORT = "collaboration_support"
    REVIEW_AUDIT = "review_audit"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(StrEnum):
    DRAFT = "draft"
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    REWORK_REQUIRED = "rework_required"
    CLOSED = "closed"


class ApplicationStatus(StrEnum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    CONVERTED_TO_GROWTH_SEAT = "converted_to_growth_seat"
    CONVERTED_TO_FORMAL_SEAT = "converted_to_formal_seat"


class SeatType(StrEnum):
    GROWTH = "growth"
    FORMAL = "formal"


class SeatStatus(StrEnum):
    PROPOSED = "proposed"
    ON_TRIAL = "on_trial"
    CONFIRMED = "confirmed"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    TERMINATED = "terminated"


class SourceType(StrEnum):
    GITHUB = "github"
    GITEE = "gitee"
    GITLAB = "gitlab"
    INTERNAL = "internal"


class SignalType(StrEnum):
    REPO_BOUND = "repo_bound"
    ISSUE_OPENED = "issue_opened"
    ISSUE_CLOSED = "issue_closed"
    PR_OPENED = "pr_opened"
    PR_MERGED = "pr_merged"
    RELEASE_CREATED = "release_created"
    MILESTONE_REACHED = "milestone_reached"
    TASK_STARTED = "task_started"
    TASK_SUBMITTED = "task_submitted"
    TASK_COMPLETED = "task_completed"
    REVIEW_PASSED = "review_passed"


class HumanReviewStatus(StrEnum):
    NONE = "none"
    REVIEWER_REQUIRED = "reviewer_required"
    REVIEWER_ASSIGNED = "reviewer_assigned"
    PENDING_REVIEW = "pending_review"
    PASSED = "passed"


class CreatedVia(StrEnum):
    WEB = "web"
    MCP = "mcp"
