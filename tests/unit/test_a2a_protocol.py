"""Tests for A2A protocol objects and agent functions."""

import pytest

from app.domain.a2a_protocol import AgentResult, DelegationContract, TaskEnvelope


class TestTaskEnvelope:
    def test_envelope_has_auto_generated_id(self):
        e = TaskEnvelope(task_id="t1", project_id="p1")
        assert e.envelope_id
        assert len(e.envelope_id) == 36  # UUID format

    def test_envelope_stores_constraints(self):
        e = TaskEnvelope(task_id="t1", project_id="p1", constraints={"ewu": "5.0"})
        assert e.constraints["ewu"] == "5.0"


class TestDelegationContract:
    def test_contract_defaults(self):
        c = DelegationContract(
            envelope_id="e1",
            delegator_agent="coord",
            delegatee_agent="match",
            delegation_type="matching",
        )
        assert c.status == "pending"
        assert "write_platform_state" in c.forbidden_actions
        assert c.timeout_seconds == 30

    def test_contract_human_checkpoint(self):
        c = DelegationContract(
            envelope_id="e1",
            delegator_agent="coord",
            delegatee_agent="vc",
            delegation_type="vc_issuance",
            human_checkpoint_required=True,
        )
        assert c.human_checkpoint_required is True


class TestAgentResult:
    def test_result_fields(self):
        r = AgentResult(
            delegation_id="d1",
            result_type="matching_suggestion",
            summary="Test",
            confidence=0.7,
        )
        assert r.confidence == 0.7
        assert r.requires_human_review is True


class TestMatchingAgent:
    @pytest.mark.asyncio
    async def test_development_task_matching(self):
        from app.services.agents.matching_agent import run_matching_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            constraints={"task_type": "development", "main_role": "developer", "ewu": "6.0"},
        )
        c = DelegationContract(
            envelope_id=e.envelope_id,
            delegator_agent="coord",
            delegatee_agent="match",
            delegation_type="matching",
        )
        r = await run_matching_agent(e, c)
        assert r.result_type == "matching_suggestion"
        assert r.structured_payload["recommended_seat_type"] == "formal"
        assert r.confidence > 0

    @pytest.mark.asyncio
    async def test_low_ewu_growth_seat(self):
        from app.services.agents.matching_agent import run_matching_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            constraints={"task_type": "development", "main_role": "developer", "ewu": "2.0"},
        )
        c = DelegationContract(
            envelope_id=e.envelope_id,
            delegator_agent="coord",
            delegatee_agent="match",
            delegation_type="matching",
        )
        r = await run_matching_agent(e, c)
        assert r.structured_payload["recommended_seat_type"] == "growth"


class TestGitHubSignalAgent:
    @pytest.mark.asyncio
    async def test_no_signals(self):
        from app.services.agents.github_signal_agent import run_github_signal_agent

        e = TaskEnvelope(task_id="t1", project_id="p1", signal_context={})
        c = DelegationContract(
            envelope_id=e.envelope_id,
            delegator_agent="coord",
            delegatee_agent="gh",
            delegation_type="github_signal",
        )
        r = await run_github_signal_agent(e, c)
        assert r.structured_payload["signal_status"] == "no_signal"
        assert r.confidence < 0.5

    @pytest.mark.asyncio
    async def test_full_signals(self):
        from app.services.agents.github_signal_agent import run_github_signal_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            signal_context={
                "repo_url": "https://github.com/test/repo",
                "branch_name": "main",
                "pr_url": "https://github.com/test/repo/pull/1",
                "latest_commit_sha": "abc123def456",
            },
        )
        c = DelegationContract(
            envelope_id=e.envelope_id,
            delegator_agent="coord",
            delegatee_agent="gh",
            delegation_type="github_signal",
        )
        r = await run_github_signal_agent(e, c)
        assert r.structured_payload["signal_status"] == "active"
        assert r.structured_payload["signal_count"] >= 3


class TestVCAgent:
    @pytest.mark.asyncio
    async def test_eligible_completed_verified(self):
        from app.services.agents.vc_agent import run_vc_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            current_status="completed",
            constraints={"ewu": "4.0"},
            signal_context={
                "verification_status": "verified",
                "completion_mode": "evidence_backed",
                "evidence_count": 2,
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
        assert r.structured_payload["issuance_basis"] == "verified"

    @pytest.mark.asyncio
    async def test_deny_not_completed(self):
        from app.services.agents.vc_agent import run_vc_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            current_status="in_progress",
            constraints={"ewu": "4.0"},
            signal_context={
                "verification_status": "unverified",
                "completion_mode": "evidence_backed",
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
        assert r.structured_payload["issuance_decision"] == "deny"

    @pytest.mark.asyncio
    async def test_legacy_completed(self):
        from app.services.agents.vc_agent import run_vc_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            current_status="completed",
            constraints={"ewu": "4.0"},
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

    @pytest.mark.asyncio
    async def test_legacy_not_completed_denied(self):
        from app.services.agents.vc_agent import run_vc_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            current_status="in_progress",
            constraints={"ewu": "4.0"},
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
        assert r.structured_payload["issuance_decision"] == "deny"


class TestReviewPrepAgent:
    @pytest.mark.asyncio
    async def test_review_prep_with_evidence(self):
        from app.services.agents.review_prep_agent import run_review_prep_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            objective="Build feature",
            completion_criteria="Tests pass",
            signal_context={"evidence_count": 2, "repo_url": "https://github.com/test"},
        )
        c = DelegationContract(
            envelope_id=e.envelope_id,
            delegator_agent="coord",
            delegatee_agent="rp",
            delegation_type="review_prep",
        )
        r = await run_review_prep_agent(e, c)
        assert r.result_type == "review_brief"
        assert "review_checklist" in r.structured_payload
        assert r.structured_payload["evidence_count"] == 2
