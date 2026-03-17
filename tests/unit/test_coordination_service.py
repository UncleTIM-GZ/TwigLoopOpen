"""Tests for coordination and delegation logic.

Covers: TaskEnvelope, DelegationContract, AgentResult field defaults,
MatchingAgent task_type matching, GitHubSignalAgent signal combinations,
and VCAgent eligibility scenarios.
"""

import uuid

import pytest

from app.domain.a2a_protocol import AgentResult, DelegationContract, TaskEnvelope


# ── TaskEnvelope defaults and construction ───────────────────────────


class TestTaskEnvelopeDefaults:
    def test_envelope_id_is_uuid_format(self) -> None:
        e = TaskEnvelope(task_id="t1", project_id="p1")
        assert len(e.envelope_id) == 36

    def test_envelope_id_unique_per_instance(self) -> None:
        e1 = TaskEnvelope(task_id="t1", project_id="p1")
        e2 = TaskEnvelope(task_id="t1", project_id="p1")
        assert e1.envelope_id != e2.envelope_id

    def test_default_constraints_is_empty_dict(self) -> None:
        e = TaskEnvelope(task_id="t1", project_id="p1")
        assert e.constraints == {}

    def test_default_evidence_requirements_is_empty_list(self) -> None:
        e = TaskEnvelope(task_id="t1", project_id="p1")
        assert e.evidence_requirements == []

    def test_default_signal_context_is_empty_dict(self) -> None:
        e = TaskEnvelope(task_id="t1", project_id="p1")
        assert e.signal_context == {}

    def test_default_current_status_is_empty(self) -> None:
        e = TaskEnvelope(task_id="t1", project_id="p1")
        assert e.current_status == ""

    def test_default_version_is_1(self) -> None:
        e = TaskEnvelope(task_id="t1", project_id="p1")
        assert e.version == 1

    def test_created_at_is_iso_string(self) -> None:
        e = TaskEnvelope(task_id="t1", project_id="p1")
        assert "T" in e.created_at  # ISO 8601 format

    def test_custom_constraints_stored(self) -> None:
        e = TaskEnvelope(task_id="t1", project_id="p1", constraints={"ewu": "5.0", "tier": "A"})
        assert e.constraints["ewu"] == "5.0"
        assert e.constraints["tier"] == "A"

    def test_work_package_id_defaults_none(self) -> None:
        e = TaskEnvelope(task_id="t1", project_id="p1")
        assert e.work_package_id is None

    def test_actor_role_defaults_none(self) -> None:
        e = TaskEnvelope(task_id="t1", project_id="p1")
        assert e.actor_role is None


# ── DelegationContract defaults and construction ─────────────────────


class TestDelegationContractDefaults:
    def test_delegation_id_is_uuid(self) -> None:
        c = DelegationContract(
            envelope_id="e1",
            delegator_agent="coord",
            delegatee_agent="match",
            delegation_type="matching",
        )
        assert len(c.delegation_id) == 36

    def test_default_status_is_pending(self) -> None:
        c = DelegationContract(
            envelope_id="e1",
            delegator_agent="coord",
            delegatee_agent="match",
            delegation_type="matching",
        )
        assert c.status == "pending"

    def test_default_timeout_is_30(self) -> None:
        c = DelegationContract(
            envelope_id="e1",
            delegator_agent="coord",
            delegatee_agent="match",
            delegation_type="matching",
        )
        assert c.timeout_seconds == 30

    def test_default_callback_mode_is_sync(self) -> None:
        c = DelegationContract(
            envelope_id="e1",
            delegator_agent="coord",
            delegatee_agent="match",
            delegation_type="matching",
        )
        assert c.callback_mode == "sync"

    def test_default_forbidden_actions_includes_write(self) -> None:
        c = DelegationContract(
            envelope_id="e1",
            delegator_agent="coord",
            delegatee_agent="match",
            delegation_type="matching",
        )
        assert "write_platform_state" in c.forbidden_actions

    def test_default_forbidden_actions_includes_issue_vc(self) -> None:
        c = DelegationContract(
            envelope_id="e1",
            delegator_agent="coord",
            delegatee_agent="match",
            delegation_type="matching",
        )
        assert "issue_vc" in c.forbidden_actions

    def test_default_allowed_actions(self) -> None:
        c = DelegationContract(
            envelope_id="e1",
            delegator_agent="coord",
            delegatee_agent="match",
            delegation_type="matching",
        )
        assert "read_only" in c.allowed_actions
        assert "suggest" in c.allowed_actions

    def test_human_checkpoint_defaults_false(self) -> None:
        c = DelegationContract(
            envelope_id="e1",
            delegator_agent="coord",
            delegatee_agent="match",
            delegation_type="matching",
        )
        assert c.human_checkpoint_required is False

    def test_idempotency_key_is_uuid(self) -> None:
        c = DelegationContract(
            envelope_id="e1",
            delegator_agent="coord",
            delegatee_agent="match",
            delegation_type="matching",
        )
        assert len(c.idempotency_key) == 36

    def test_idempotency_key_unique_per_instance(self) -> None:
        c1 = DelegationContract(
            envelope_id="e1",
            delegator_agent="coord",
            delegatee_agent="match",
            delegation_type="matching",
        )
        c2 = DelegationContract(
            envelope_id="e1",
            delegator_agent="coord",
            delegatee_agent="match",
            delegation_type="matching",
        )
        assert c1.idempotency_key != c2.idempotency_key


# ── AgentResult defaults and construction ────────────────────────────


class TestAgentResultDefaults:
    def test_default_confidence_is_zero(self) -> None:
        r = AgentResult(delegation_id="d1", result_type="test")
        assert r.confidence == 0.0

    def test_default_requires_human_review_is_true(self) -> None:
        r = AgentResult(delegation_id="d1", result_type="test")
        assert r.requires_human_review is True

    def test_default_structured_payload_is_empty_dict(self) -> None:
        r = AgentResult(delegation_id="d1", result_type="test")
        assert r.structured_payload == {}

    def test_default_summary_is_empty(self) -> None:
        r = AgentResult(delegation_id="d1", result_type="test")
        assert r.summary == ""

    def test_produced_at_is_iso_string(self) -> None:
        r = AgentResult(delegation_id="d1", result_type="test")
        assert "T" in r.produced_at

    def test_custom_confidence_stored(self) -> None:
        r = AgentResult(delegation_id="d1", result_type="test", confidence=0.85)
        assert r.confidence == 0.85


# ── MatchingAgent task_type matching ─────────────────────────────────


class TestMatchingAgentMatching:
    async def test_development_task_recommends_formal_high_ewu(self) -> None:
        from app.services.agents.matching_agent import run_matching_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            constraints={"task_type": "development", "main_role": "developer", "ewu": "7.0"},
        )
        c = DelegationContract(
            envelope_id=e.envelope_id,
            delegator_agent="coord",
            delegatee_agent="match",
            delegation_type="matching",
        )
        r = await run_matching_agent(e, c)
        assert r.structured_payload["recommended_seat_type"] == "formal"
        assert r.structured_payload["complexity_level"] == "high"

    async def test_development_task_low_ewu_recommends_growth(self) -> None:
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

    async def test_product_design_task_matching(self) -> None:
        from app.services.agents.matching_agent import run_matching_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            constraints={"task_type": "product_design", "main_role": "designer", "ewu": "3.0"},
        )
        c = DelegationContract(
            envelope_id=e.envelope_id,
            delegator_agent="coord",
            delegatee_agent="match",
            delegation_type="matching",
        )
        r = await run_matching_agent(e, c)
        assert r.result_type == "matching_suggestion"
        assert "designer" in r.structured_payload["skill_requirements"]

    async def test_unknown_task_type_handled(self) -> None:
        from app.services.agents.matching_agent import run_matching_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            constraints={"task_type": "research", "main_role": "analyst", "ewu": "4.0"},
        )
        c = DelegationContract(
            envelope_id=e.envelope_id,
            delegator_agent="coord",
            delegatee_agent="match",
            delegation_type="matching",
        )
        r = await run_matching_agent(e, c)
        assert r.result_type == "matching_suggestion"
        assert r.confidence > 0


# ── GitHubSignalAgent signal combinations ────────────────────────────


class TestGitHubSignalAgentCombinations:
    async def test_no_signals_returns_no_signal(self) -> None:
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
        assert r.structured_payload["signal_count"] == 0

    async def test_repo_only_returns_partial(self) -> None:
        from app.services.agents.github_signal_agent import run_github_signal_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            signal_context={"repo_url": "https://github.com/org/repo"},
        )
        c = DelegationContract(
            envelope_id=e.envelope_id,
            delegator_agent="coord",
            delegatee_agent="gh",
            delegation_type="github_signal",
        )
        r = await run_github_signal_agent(e, c)
        assert r.structured_payload["signal_status"] == "partial"
        assert r.structured_payload["signal_count"] == 1

    async def test_repo_and_branch_returns_partial(self) -> None:
        from app.services.agents.github_signal_agent import run_github_signal_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            signal_context={
                "repo_url": "https://github.com/org/repo",
                "branch_name": "feat/auth",
            },
        )
        c = DelegationContract(
            envelope_id=e.envelope_id,
            delegator_agent="coord",
            delegatee_agent="gh",
            delegation_type="github_signal",
        )
        r = await run_github_signal_agent(e, c)
        assert r.structured_payload["signal_status"] == "partial"
        assert r.structured_payload["signal_count"] == 2

    async def test_three_signals_returns_active(self) -> None:
        from app.services.agents.github_signal_agent import run_github_signal_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            signal_context={
                "repo_url": "https://github.com/org/repo",
                "branch_name": "main",
                "pr_url": "https://github.com/org/repo/pull/5",
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

    async def test_confidence_high_with_full_signals(self) -> None:
        from app.services.agents.github_signal_agent import run_github_signal_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            signal_context={
                "repo_url": "https://github.com/org/repo",
                "branch_name": "main",
                "pr_url": "https://github.com/org/repo/pull/1",
                "latest_commit_sha": "abc123",
            },
        )
        c = DelegationContract(
            envelope_id=e.envelope_id,
            delegator_agent="coord",
            delegatee_agent="gh",
            delegation_type="github_signal",
        )
        r = await run_github_signal_agent(e, c)
        assert r.confidence >= 0.8


# ── VCAgent eligibility scenarios ────────────────────────────────────


class TestVCAgentEligibility:
    async def test_completed_verified_with_evidence_eligible(self) -> None:
        from app.services.agents.vc_agent import run_vc_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            current_status="completed",
            constraints={"ewu": "5.0"},
            signal_context={
                "verification_status": "verified",
                "completion_mode": "evidence_backed",
                "evidence_count": 3,
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

    async def test_not_completed_denied(self) -> None:
        from app.services.agents.vc_agent import run_vc_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            current_status="submitted",
            constraints={"ewu": "3.0"},
            signal_context={
                "verification_status": "verified",
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

    async def test_no_evidence_denied(self) -> None:
        from app.services.agents.vc_agent import run_vc_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            current_status="completed",
            constraints={"ewu": "3.0"},
            signal_context={
                "verification_status": "verified",
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

    async def test_vc_result_includes_ewu(self) -> None:
        from app.services.agents.vc_agent import run_vc_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            current_status="completed",
            constraints={"ewu": "6.50"},
            signal_context={
                "verification_status": "verified",
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
        assert r.structured_payload["ewu"] == 6.5

    async def test_eligible_confidence_higher_than_denied(self) -> None:
        from app.services.agents.vc_agent import run_vc_agent

        e_ok = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            current_status="completed",
            constraints={"ewu": "3.0"},
            signal_context={
                "verification_status": "verified",
                "completion_mode": "evidence_backed",
                "evidence_count": 1,
            },
        )
        e_deny = TaskEnvelope(
            task_id="t2",
            project_id="p1",
            current_status="in_progress",
            constraints={"ewu": "3.0"},
            signal_context={
                "verification_status": "unverified",
                "completion_mode": "evidence_backed",
                "evidence_count": 0,
            },
        )
        c = DelegationContract(
            envelope_id=e_ok.envelope_id,
            delegator_agent="coord",
            delegatee_agent="vc",
            delegation_type="vc_issuance",
        )
        r_ok = await run_vc_agent(e_ok, c)
        c2 = DelegationContract(
            envelope_id=e_deny.envelope_id,
            delegator_agent="coord",
            delegatee_agent="vc",
            delegation_type="vc_issuance",
        )
        r_deny = await run_vc_agent(e_deny, c2)
        assert r_ok.confidence >= r_deny.confidence
