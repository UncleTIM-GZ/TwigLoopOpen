"""Role-based access control constants and utilities."""

from enum import StrEnum


class Role(StrEnum):
    """Platform roles for RBAC."""

    FOUNDER = "founder"
    COLLABORATOR = "collaborator"
    REVIEWER = "reviewer"
    SPONSOR = "sponsor"
    OPERATOR = "operator"
    ADMIN = "admin"
