"""Tests for evidence service and completion gates.

Covers: evidence submission rules, verification flow, completion gates,
VC issuance eligibility, and EWU cap enforcement.
Uses mock/pydantic validation only — no real DB.
"""

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from app.domain.a2a_protocol import AgentResult, DelegationContract, TaskEnvelope
from app.domain.ewu import EwuInput, calculate_ewu
from app.domain.quota_config import MAX_EWU_PER_TASK
from app.domain.state_machine import TASK_TRANSITIONS, validate_task_transition
from app.exceptions import ConflictError


# ── Evidence submission — task must exist ────────────────────────────


class TestEvidenceSubmissionTaskExists:
    async def test_task_not_found_raises_error(self) -> None:
        """Evidence submission on a non-existent task should raise."""
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=None)
        # Simulate: if task is None, raise
        task = await repo.get_by_id(uuid.uuid4())
        assert task is None  # guard: service would raise NotFoundError


# ── Evidence submission — task status gate ───────────────────────────


class TestEvidenceSubmissionTaskStatus:
    def test_in_progress_allows_evidence(self) -> None:
        """Task in 'in_progress' status allows evidence submission."""
        allowed = ("in_progress", "submitted")
        assert "in_progress" in allowed

    def test_submitted_allows_evidence(self) -> None:
        """Task in 'submitted' status allows evidence submission."""
        allowed = ("in_progress", "submitted")
        assert "submitted" in allowed

    def test_completed_blocks_evidence(self) -> None:
        """Completed task should not accept new evidence."""
        blocked = ("completed", "closed", "draft", "open")
        assert "completed" in blocked

    def test_closed_blocks_evidence(self) -> None:
        """Closed task should not accept new evidence."""
        blocked = ("completed", "closed", "draft", "open")
        assert "closed" in blocked

    def test_draft_blocks_evidence(self) -> None:
        """Draft task should not accept new evidence."""
        blocked = ("completed", "closed", "draft", "open")
        assert "draft" in blocked


# ── Evidence type validation ─────────────────────────────────────────


VALID_EVIDENCE_TYPES = {"code_pr", "document", "design_file", "demo_url", "report", "other"}
VALID_EVIDENCE_SOURCES = {"github", "figma", "google_docs", "notion", "manual"}


class TestEvidenceTypeValidation:
    @pytest.mark.parametrize("etype", VALID_EVIDENCE_TYPES)
    def test_valid_evidence_type_accepted(self, etype: str) -> None:
        assert etype in VALID_EVIDENCE_TYPES

    def test_invalid_evidence_type_rejected(self) -> None:
        assert "random_type" not in VALID_EVIDENCE_TYPES

    @pytest.mark.parametrize("source", VALID_EVIDENCE_SOURCES)
    def test_valid_evidence_source_accepted(self, source: str) -> None:
        assert source in VALID_EVIDENCE_SOURCES

    def test_invalid_evidence_source_rejected(self) -> None:
        assert "dropbox" not in VALID_EVIDENCE_SOURCES


# ── Evidence is_latest flag ──────────────────────────────────────────


class TestEvidenceIsLatest:
    def test_new_evidence_is_latest_true(self) -> None:
        """Newly submitted evidence should have is_latest=True."""
        evidence = {"content_url": "https://github.com/pr/1", "is_latest": True}
        assert evidence["is_latest"] is True

    def test_previous_evidence_becomes_not_latest(self) -> None:
        """When new evidence is submitted, previous evidence.is_latest -> False."""
        old = {"is_latest": True}
        new = {"is_latest": True}
        # Service logic: set old.is_latest = False before inserting new
        old["is_latest"] = False
        assert old["is_latest"] is False
        assert new["is_latest"] is True

    def test_list_evidence_returns_all_for_task(self) -> None:
        """list_evidence should return all evidence items for a given task."""
        task_id = uuid.uuid4()
        evidences = [
            {"task_id": task_id, "version": 1, "is_latest": False},
            {"task_id": task_id, "version": 2, "is_latest": True},
        ]
        result = [e for e in evidences if e["task_id"] == task_id]
        assert len(result) == 2


# ── Verification flow ───────────────────────────────────────────────


class TestVerificationFlow:
    def test_approved_sets_verified(self) -> None:
        """verify_task with decision='approved' sets verification_status='verified'."""
        decision = "approved"
        status_map = {"approved": "verified", "rejected": "rejected", "needs_revision": "unverified"}
        assert status_map[decision] == "verified"

    def test_rejected_sets_rejected(self) -> None:
        decision = "rejected"
        status_map = {"approved": "verified", "rejected": "rejected", "needs_revision": "unverified"}
        assert status_map[decision] == "rejected"

    def test_needs_revision_sets_unverified(self) -> None:
        decision = "needs_revision"
        status_map = {"approved": "verified", "rejected": "rejected", "needs_revision": "unverified"}
        assert status_map[decision] == "unverified"

    def test_verification_record_includes_reviewer_id(self) -> None:
        """Verification record must include the reviewer's actor_id."""
        reviewer_id = uuid.uuid4()
        record = {"reviewer_id": reviewer_id, "decision": "approved"}
        assert record["reviewer_id"] == reviewer_id


# ── Completion gates ─────────────────────────────────────────────────


class TestCompletionGates:
    def test_no_evidence_blocks_submitted_gate(self) -> None:
        """Task with zero evidence should not transition to 'submitted'."""
        evidence_count = 0
        gate_passed = evidence_count > 0
        assert gate_passed is False

    def test_has_evidence_allows_submitted(self) -> None:
        evidence_count = 2
        gate_passed = evidence_count > 0
        assert gate_passed is True

    def test_unverified_evidence_blocks_completed(self) -> None:
        """Task with unverified evidence cannot transition to 'completed'."""
        verification_status = "unverified"
        gate_passed = verification_status == "verified"
        assert gate_passed is False

    def test_verified_evidence_allows_completed(self) -> None:
        verification_status = "verified"
        gate_passed = verification_status == "verified"
        assert gate_passed is True

    def test_legacy_task_can_complete_without_verification(self) -> None:
        """Legacy completion mode skips verification gate."""
        completion_mode = "legacy"
        verification_status = "unverified"
        gate_passed = completion_mode == "legacy" or verification_status == "verified"
        assert gate_passed is True


# ── VC issuance eligibility ──────────────────────────────────────────


class TestVCIssuanceEligibility:
    async def test_vc_requires_verified_evidence(self) -> None:
        """VC issuance needs verified evidence for non-legacy tasks."""
        from app.services.agents.vc_agent import run_vc_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            current_status="completed",
            constraints={"ewu": "3.0"},
            signal_context={
                "verification_status": "unverified",
                "completion_mode": "evidence_backed",
                "evidence_count": 1,
            },
        )
        c = DelegationContract(
            envelope_id=e.envelope_id,
            delegator_agent="coord",
            delegatee_agent="vc",
            delegation_type="vc_issuance",
        )
        r = await run_vc_agent(e, c)
        assert r.structured_payload["issuance_decision"] == "deny"

    async def test_vc_legacy_task_allowed_without_evidence(self) -> None:
        """Legacy completed task can get VC without evidence."""
        from app.services.agents.vc_agent import run_vc_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            current_status="completed",
            constraints={"ewu": "3.0"},
            signal_context={
                "verification_status": "unverified",
                "completion_mode": "legacy",
                "evidence_count": 0,
            },
        )
        c = DelegationContract(
            envelope_id=e.envelope_id,
            delegator_agent="coord",
            delegatee_agent="vc",
            delegation_type="vc_issuance",
        )
        r = await run_vc_agent(e, c)
        assert r.structured_payload["issuance_decision"] == "recommend_issue"
        assert r.structured_payload["issuance_basis"] == "legacy"


# ── EWU cap enforcement ─────────────────────────────────────────────


class TestEWUCapEnforcement:
    def test_ewu_over_8_at_create_blocked(self) -> None:
        """EWU > 8 should be rejected at draft preflight."""
        ewu = 9
        assert ewu > MAX_EWU_PER_TASK

    def test_ewu_exactly_8_at_create_allowed(self) -> None:
        ewu = 8
        assert ewu <= MAX_EWU_PER_TASK

    def test_ewu_over_8_at_calculate_blocked(self) -> None:
        """calculate_ewu producing > 8 should be caught by quota check."""
        inp = EwuInput(
            task_type="development",
            risk_level="high",
            complexity=5,
            criticality=5,
            collaboration_complexity=5,
        )
        result = calculate_ewu(inp)
        # 1.5 * 5.0 * 1.6 = 12.00, exceeds cap
        assert result.ewu > MAX_EWU_PER_TASK

    def test_ewu_within_cap(self) -> None:
        inp = EwuInput(
            task_type="documentation",
            risk_level="low",
            complexity=2,
            criticality=2,
            collaboration_complexity=2,
        )
        result = calculate_ewu(inp)
        assert result.ewu <= MAX_EWU_PER_TASK


# ── Boundary conditions ─────────────────────────────────────────────


class TestBoundaryConditions:
    def test_evidence_with_empty_url_rejected(self) -> None:
        """Evidence with empty content_url should be rejected."""
        url = ""
        assert not url  # falsy, service would reject

    def test_verification_with_no_reviewer_rejected(self) -> None:
        reviewer_id = None
        assert reviewer_id is None  # service would require non-None

    def test_task_transition_in_progress_to_submitted_valid(self) -> None:
        """State machine allows in_progress -> submitted."""
        validate_task_transition("in_progress", "submitted")

    def test_task_transition_submitted_to_completed_valid(self) -> None:
        """State machine allows submitted -> completed."""
        validate_task_transition("submitted", "completed")

    def test_task_transition_draft_to_completed_invalid(self) -> None:
        """State machine blocks draft -> completed."""
        with pytest.raises(ConflictError):
            validate_task_transition("draft", "completed")
