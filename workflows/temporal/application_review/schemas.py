"""Schemas for the application review workflow."""

from dataclasses import dataclass


@dataclass
class ApplicationReviewInput:
    token: str
    project_id: str
    applicant_actor_id: str
    motivation: str
    preferred_role: str = "collaborator"


@dataclass
class ReviewDecision:
    """Signal payload for founder's review decision."""

    decision: str  # "approved", "rejected"
    reason: str = ""
    seat_type: str = "growth"  # "growth" or "formal"


@dataclass
class ApplicationReviewResult:
    application_id: str
    decision: str  # "approved", "rejected", "expired"
    seat_id: str | None = None


# Activity-level dataclasses

@dataclass
class CreateApplicationInput:
    token: str
    project_id: str
    motivation: str
    preferred_role: str


@dataclass
class NotifyFounderInput:
    project_id: str
    application_id: str


@dataclass
class ApproveApplicationInput:
    token: str
    application_id: str
    project_id: str
    actor_id: str
    seat_type: str


@dataclass
class RejectApplicationInput:
    token: str
    application_id: str
    reason: str


@dataclass
class ExpireApplicationInput:
    token: str
    application_id: str
