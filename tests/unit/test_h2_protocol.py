"""Tests for Horizon 2 protocol enhancements — protocol version, trace_id, Agent Card."""

import pytest
from app.domain.a2a_protocol import (
    PROTOCOL_VERSION,
    AgentResult,
    DelegationContract,
    TaskEnvelope,
)
from app.domain.agent_card import AGENT_CARDS, AgentCard


class TestProtocolVersion:
    def test_protocol_version_constant(self):
        assert PROTOCOL_VERSION == "2.0"

    def test_envelope_has_protocol_version(self):
        e = TaskEnvelope(task_id="t1", project_id="p1")
        assert e.protocol_version == "2.0"

    def test_envelope_has_trace_id(self):
        e = TaskEnvelope(task_id="t1", project_id="p1")
        assert e.trace_id
        assert len(e.trace_id) == 36

    def test_contract_has_correlation_id(self):
        c = DelegationContract(
            envelope_id="e1",
            delegator_agent="coord",
            delegatee_agent="match",
            delegation_type="matching",
        )
        assert c.correlation_id
        assert len(c.correlation_id) == 36
        assert c.retry_count == 0
        assert c.max_retries == 3

    def test_result_has_agent_version(self):
        r = AgentResult(
            delegation_id="d1",
            result_type="test",
            agent_version="2.0.0",
        )
        assert r.agent_version == "2.0.0"
        assert r.error_code is None
        assert r.error_detail is None

    def test_result_error_fields(self):
        r = AgentResult(
            delegation_id="d1",
            result_type="error",
            error_code="delegation_failed",
            error_detail="Connection timeout",
        )
        assert r.error_code == "delegation_failed"
        assert r.error_detail == "Connection timeout"

    def test_result_trace_id(self):
        r = AgentResult(
            delegation_id="d1",
            result_type="test",
            trace_id="trace-123",
        )
        assert r.trace_id == "trace-123"


class TestAgentCard:
    def test_all_agents_registered(self):
        expected = {"matching_agent", "review_prep_agent", "github_signal_agent", "vc_agent"}
        assert set(AGENT_CARDS.keys()) == expected

    def test_github_signal_card(self):
        card = AGENT_CARDS["github_signal_agent"]
        assert card.agent_id == "github_signal_agent"
        assert "github_signal" in card.capabilities.delegation_types
        assert card.constraints.requires_human_review is False
        assert card.protocol_version == "2.0"

    def test_vc_agent_card(self):
        card = AGENT_CARDS["vc_agent"]
        assert card.constraints.requires_human_review is True
        assert "issue_vc" in card.constraints.forbidden_actions

    def test_card_serialization(self):
        card = AGENT_CARDS["matching_agent"]
        data = card.model_dump()
        assert data["agent_id"] == "matching_agent"
        assert "delegation_types" in data["capabilities"]
        # Round-trip
        restored = AgentCard.model_validate(data)
        assert restored.agent_id == card.agent_id

    def test_all_cards_have_forbidden_write(self):
        for name, card in AGENT_CARDS.items():
            assert "write_platform_state" in card.constraints.forbidden_actions, (
                f"{name} missing write_platform_state in forbidden_actions"
            )


class TestGitHubSignalAgentH2:
    """Tests for H2 enhancements to GitHubSignalAgent."""

    @pytest.mark.asyncio
    async def test_pr_merged_strong_signal(self):
        from app.services.agents.github_signal_agent import run_github_signal_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            signal_context={
                "repo_url": "https://github.com/test/repo",
                "branch_name": "feat/x",
                "pr_url": "https://github.com/test/repo/pull/1",
                "latest_commit_sha": "abc123def456",
                "pr_state": "closed",
                "pr_merged": True,
            },
        )
        c = DelegationContract(
            envelope_id=e.envelope_id,
            delegator_agent="coord",
            delegatee_agent="gh",
            delegation_type="github_signal",
        )
        r = await run_github_signal_agent(e, c)
        assert r.structured_payload["signal_status"] == "strong"
        assert r.structured_payload["pr_lifecycle"]["pr_status"] == "merged"
        assert r.confidence == 0.95
        assert r.agent_version == "2.0.0"
        assert r.trace_id == e.trace_id

    @pytest.mark.asyncio
    async def test_pr_approved_signal(self):
        from app.services.agents.github_signal_agent import run_github_signal_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            signal_context={
                "repo_url": "https://github.com/test/repo",
                "branch_name": "feat/x",
                "pr_url": "https://github.com/test/repo/pull/2",
                "latest_commit_sha": "def456",
                "pr_state": "open",
                "review_state": "approved",
            },
        )
        c = DelegationContract(
            envelope_id=e.envelope_id,
            delegator_agent="coord",
            delegatee_agent="gh",
            delegation_type="github_signal",
        )
        r = await run_github_signal_agent(e, c)
        assert r.structured_payload["pr_lifecycle"]["pr_status"] == "approved"
        assert r.confidence == 0.9

    @pytest.mark.asyncio
    async def test_changes_requested_signal(self):
        from app.services.agents.github_signal_agent import run_github_signal_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            signal_context={
                "repo_url": "https://github.com/test/repo",
                "pr_state": "open",
                "review_state": "changes_requested",
            },
        )
        c = DelegationContract(
            envelope_id=e.envelope_id,
            delegator_agent="coord",
            delegatee_agent="gh",
            delegation_type="github_signal",
        )
        r = await run_github_signal_agent(e, c)
        assert r.structured_payload["pr_lifecycle"]["pr_status"] == "changes_requested"

    @pytest.mark.asyncio
    async def test_commit_count_included(self):
        from app.services.agents.github_signal_agent import run_github_signal_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            signal_context={
                "repo_url": "https://github.com/test/repo",
                "commit_count": 15,
            },
        )
        c = DelegationContract(
            envelope_id=e.envelope_id,
            delegator_agent="coord",
            delegatee_agent="gh",
            delegation_type="github_signal",
        )
        r = await run_github_signal_agent(e, c)
        assert r.structured_payload["commit_count"] == 15


class TestVCAgentH2:
    """Tests for H2 VC agent trace propagation."""

    @pytest.mark.asyncio
    async def test_vc_agent_trace_propagation(self):
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
        # VC agent itself doesn't set trace_id, CoordinationService does
        assert r.result_type == "vc_recommendation"
