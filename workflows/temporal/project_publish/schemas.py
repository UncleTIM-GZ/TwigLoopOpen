"""Schemas for the project publish workflow."""

from dataclasses import dataclass, field


@dataclass
class TaskInput:
    title: str
    task_type: str
    goal: str
    output_spec: str
    completion_criteria: str
    main_role: str
    risk_level: str = "low"
    ewu: float = 1.0


@dataclass
class WorkPackageInput:
    title: str
    description: str | None = None
    tasks: list[TaskInput] = field(default_factory=list)


@dataclass
class PublishProjectInput:
    token: str
    project_type: str
    founder_type: str
    title: str
    summary: str
    work_packages: list[WorkPackageInput] = field(default_factory=list)
    target_users: str | None = None


@dataclass
class PublishProjectResult:
    project_id: str
    work_package_ids: list[str] = field(default_factory=list)
    task_ids: list[str] = field(default_factory=list)


# Activity-level dataclasses

@dataclass
class CreateProjectInput:
    token: str
    project_type: str
    founder_type: str
    title: str
    summary: str
    target_users: str | None = None


@dataclass
class CreateWorkPackageInput:
    token: str
    project_id: str
    title: str
    description: str | None = None
    sort_order: int = 0


@dataclass
class CreateTaskCardInput:
    token: str
    work_package_id: str
    title: str
    task_type: str
    goal: str
    output_spec: str
    completion_criteria: str
    main_role: str
    risk_level: str = "low"
    ewu: float = 1.0


@dataclass
class MarkProjectDraftInput:
    token: str
    project_id: str



# Re-export from shared for backward compatibility
from temporal.shared_schemas import PublishEventInput as PublishEventInput  # noqa: E402, F401
