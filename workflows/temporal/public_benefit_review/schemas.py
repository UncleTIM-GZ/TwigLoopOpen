"""Schemas for the public benefit review workflow."""

from dataclasses import dataclass


@dataclass
class PublicBenefitReviewInput:
    token: str
    project_id: str
    milestone: str
    reviewer_id: str


@dataclass
class ReviewResult:
    """Signal payload for reviewer's decision."""

    decision: str  # "passed", "needs_revision", "rejected"
    feedback: str = ""


@dataclass
class PublicBenefitReviewOutput:
    project_id: str
    milestone: str
    decision: str  # "passed", "needs_revision", "rejected", "expired"


# Activity-level dataclasses

@dataclass
class MarkReviewRequiredInput:
    token: str
    project_id: str
    milestone: str


@dataclass
class NotifyReviewerInput:
    project_id: str
    reviewer_id: str
    milestone: str


@dataclass
class UpdateProjectReviewPassedInput:
    token: str
    project_id: str


@dataclass
class RequestRevisionInput:
    token: str
    project_id: str
    feedback: str


@dataclass
class RejectProjectInput:
    token: str
    project_id: str
    reason: str
