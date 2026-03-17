"""A2A protocol objects — TaskEnvelope, DelegationContract, AgentResult.

These are Twig Loop's domain protocol objects for agent-to-agent collaboration.
Phase 4 minimum: platform-internal coordination, not yet external A2A service.
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class TaskEnvelope(BaseModel):
    """Context bundle for agent collaboration around a task.

    All ID fields (envelope_id, task_id, project_id, etc.) expect UUID format strings.
    """

    envelope_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    project_id: str
    work_package_id: str | None = None
    actor_id: str | None = None
    actor_role: str | None = None  # founder, collaborator, reviewer
    objective: str = ""
    current_status: str = ""
    constraints: dict[str, Any] = Field(default_factory=dict)
    completion_criteria: str = ""
    evidence_requirements: list[str] = Field(default_factory=list)
    signal_context: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    version: int = 1


class DelegationContract(BaseModel):
    """Contract between delegator and delegatee agent.

    delegation_id and idempotency_key are auto-generated UUIDs.
    """

    delegation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    envelope_id: str
    delegator_agent: str  # e.g. "platform_coordinator"
    delegatee_agent: str  # e.g. "matching_agent"
    delegation_type: str  # "matching", "review_prep", "signal_check"
    requested_output: str = ""
    allowed_actions: list[str] = Field(default_factory=lambda: ["read_only", "suggest"])
    forbidden_actions: list[str] = Field(
        default_factory=lambda: ["write_platform_state", "issue_vc"]
    )
    timeout_seconds: int = 30
    idempotency_key: str = Field(default_factory=lambda: str(uuid.uuid4()))
    callback_mode: str = "sync"  # sync, async, webhook
    human_checkpoint_required: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    status: str = "pending"  # pending, in_progress, completed, failed, timed_out


class AgentResult(BaseModel):
    """Result returned by a specialized agent."""

    delegation_id: str
    result_type: str  # "matching_suggestion", "review_brief", "signal_summary"
    summary: str = ""
    structured_payload: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0  # 0.0 to 1.0
    requires_human_review: bool = True
    produced_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
