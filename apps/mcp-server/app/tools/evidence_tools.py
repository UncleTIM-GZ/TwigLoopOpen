"""MCP tools for delivery evidence and verification — Phase 3."""

from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from app.clients.core_api import call_core_api


def register_evidence_tools(mcp: FastMCP) -> None:
    """Register evidence and verification tools on the MCP server."""

    @mcp.tool(
        title="Submit Delivery Evidence",
        annotations=ToolAnnotations(
            readOnlyHint=False, idempotentHint=False, openWorldHint=False
        ),
    )
    async def submit_evidence(
        access_token: str,
        task_id: str,
        evidence_type: str,
        title: str,
        evidence_url: str,
        description: str = "",
        evidence_source: str = "manual",
    ) -> dict[str, Any]:
        """Submit delivery evidence for a task.

        After completing work on a task, use this to submit proof of your
        deliverables. The task must be in 'in_progress' or 'submitted' state.
        At least one evidence is required before a task can be submitted.

        Args:
            access_token: JWT access token.
            task_id: UUID of the task.
            evidence_type: One of "code_pr", "document", "design_file",
                "demo_url", "report", or "other".
            title: Brief title for this evidence (e.g. "API implementation PR").
            evidence_url: URL to the deliverable (PR link, doc link, etc.).
            description: Optional detailed description.
            evidence_source: One of "github", "figma", "google_docs",
                "notion", or "manual".
        """
        body: dict[str, str] = {
            "evidence_type": evidence_type,
            "title": title,
            "evidence_url": evidence_url,
            "evidence_source": evidence_source,
        }
        if description:
            body["description"] = description
        return await call_core_api(
            "POST",
            f"/api/v1/tasks/{task_id}/evidence",
            token=access_token,
            json_body=body,
        )

    @mcp.tool(
        title="Get Task Evidence",
        annotations=ToolAnnotations(
            readOnlyHint=True, idempotentHint=True, openWorldHint=False
        ),
    )
    async def get_task_evidence(
        task_id: str,
    ) -> dict[str, Any]:
        """List all delivery evidence submitted for a task.

        Args:
            task_id: UUID of the task.
        """
        return await call_core_api(
            "GET",
            f"/api/v1/tasks/{task_id}/evidence",
        )

    @mcp.tool(
        title="Verify Task Evidence",
        annotations=ToolAnnotations(
            readOnlyHint=False, idempotentHint=False, openWorldHint=False
        ),
    )
    async def verify_task(
        access_token: str,
        task_id: str,
        decision: str,
        note: str = "",
    ) -> dict[str, Any]:
        """Review and verify task evidence as a project founder or reviewer.

        This is the reviewer decision on whether the submitted evidence meets
        the task's completion criteria.

        Args:
            access_token: JWT access token (must be founder or reviewer).
            task_id: UUID of the task to verify.
            decision: One of "approved", "needs_revision", or "rejected".
            note: Optional reviewer note explaining the decision.
        """
        body: dict[str, str] = {"decision": decision}
        if note:
            body["note"] = note
        return await call_core_api(
            "POST",
            f"/api/v1/tasks/{task_id}/verify",
            token=access_token,
            json_body=body,
        )

    @mcp.tool(
        title="Get Task Verifications",
        annotations=ToolAnnotations(
            readOnlyHint=True, idempotentHint=True, openWorldHint=False
        ),
    )
    async def get_task_verifications(
        task_id: str,
    ) -> dict[str, Any]:
        """List all verification records for a task.

        Args:
            task_id: UUID of the task.
        """
        return await call_core_api(
            "GET",
            f"/api/v1/tasks/{task_id}/verification",
        )

    @mcp.tool(
        title="Transition Task Status",
        annotations=ToolAnnotations(
            readOnlyHint=False, idempotentHint=False, openWorldHint=False
        ),
    )
    async def transition_task_status(
        access_token: str,
        task_id: str,
        target_status: str,
    ) -> dict[str, Any]:
        """Transition a task to a new status.

        Status flow: draft → open → assigned → in_progress → submitted →
        under_review → completed. Gates enforced:
        - submitted: requires at least 1 evidence
        - completed: requires verification_status = 'verified'

        Args:
            access_token: JWT access token (must be project founder).
            task_id: UUID of the task.
            target_status: Target status to transition to.
        """
        return await call_core_api(
            "PATCH",
            f"/api/v1/tasks/{task_id}/status",
            token=access_token,
            json_body={"status": target_status},
        )

    @mcp.tool(
        title="Calculate Task EWU",
        annotations=ToolAnnotations(
            readOnlyHint=False, idempotentHint=True, openWorldHint=False
        ),
    )
    async def calculate_ewu(
        access_token: str,
        task_id: str,
        task_type: str,
        risk_level: str = "low",
        complexity: int = 3,
        criticality: int = 3,
        collaboration_complexity: int = 2,
    ) -> dict[str, Any]:
        """Calculate and set EWU for a task using the official formula.

        EWU = base_weight(task_type) × avg(complexity, criticality,
        collaboration_complexity) × risk_multiplier(risk_level).

        This is the only way to set EWU — it cannot be set manually.

        Args:
            access_token: JWT access token.
            task_id: UUID of the task.
            task_type: One of "development", "product_design", "research",
                "testing_fix", "review_audit", "requirement_clarification",
                "documentation", "collaboration_support".
            risk_level: "low" (1.0x), "medium" (1.3x), or "high" (1.6x).
            complexity: Task complexity 1-5.
            criticality: Task criticality 1-5.
            collaboration_complexity: Collaboration complexity 1-5.
        """
        return await call_core_api(
            "POST",
            f"/api/v1/tasks/{task_id}/calculate-ewu",
            token=access_token,
            json_body={
                "task_type": task_type,
                "risk_level": risk_level,
                "complexity": complexity,
                "criticality": criticality,
                "collaboration_complexity": collaboration_complexity,
            },
        )
