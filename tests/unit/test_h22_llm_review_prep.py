"""Tests for Horizon 2.2 — LLM-enhanced ReviewPrepAgent dual-track."""

from unittest.mock import AsyncMock, patch

import pytest
from app.domain.a2a_protocol import DelegationContract, TaskEnvelope
from app.services.agents.review_prep_agent import (
    _build_llm_prompt,
    _build_rule_based_brief,
    run_review_prep_agent,
)


def _make_envelope(**overrides):
    defaults = {
        "task_id": "t1",
        "project_id": "p1",
        "objective": "Build user authentication module",
        "current_status": "submitted",
        "completion_criteria": "All tests pass, code reviewed, documentation updated",
        "evidence_requirements": ["code_pr", "document"],
        "signal_context": {
            "evidence_count": 2,
            "repo_url": "https://github.com/test/repo",
            "ewu": "5.0",
        },
    }
    defaults.update(overrides)
    return TaskEnvelope(**defaults)


def _make_contract(envelope):
    return DelegationContract(
        envelope_id=envelope.envelope_id,
        delegator_agent="coord",
        delegatee_agent="review_prep",
        delegation_type="review_prep",
    )


class TestRuleBasedBrief:
    """Rule-based brief should always work (fallback)."""

    def test_basic_brief(self):
        e = _make_envelope()
        c = _make_contract(e)
        r = _build_rule_based_brief(e, c)
        assert r.result_type == "review_brief"
        assert r.structured_payload["brief_source"] == "rule_based"
        assert r.structured_payload["evidence_count"] == 2
        assert r.structured_payload["has_repo"] is True
        assert len(r.structured_payload["review_checklist"]) == 4

    def test_no_evidence(self):
        e = _make_envelope(signal_context={"evidence_count": 0})
        c = _make_contract(e)
        r = _build_rule_based_brief(e, c)
        assert r.structured_payload["evidence_count"] == 0
        assert "Wait for evidence" in r.structured_payload["recommendation"]

    def test_brief_source_field(self):
        e = _make_envelope()
        c = _make_contract(e)
        r = _build_rule_based_brief(e, c)
        assert r.structured_payload["brief_source"] == "rule_based"

    def test_agent_version(self):
        e = _make_envelope()
        c = _make_contract(e)
        r = _build_rule_based_brief(e, c)
        assert r.agent_version == "2.2.0"


class TestLLMPromptBuilding:
    """Test the prompt construction (no LLM call)."""

    def test_prompt_includes_objective(self):
        e = _make_envelope()
        prompt = _build_llm_prompt(e)
        assert "Build user authentication module" in prompt

    def test_prompt_includes_criteria(self):
        e = _make_envelope()
        prompt = _build_llm_prompt(e)
        assert "All tests pass" in prompt

    def test_prompt_includes_evidence_count(self):
        e = _make_envelope()
        prompt = _build_llm_prompt(e)
        assert "Evidence submitted: 2 items" in prompt

    def test_prompt_includes_repo(self):
        e = _make_envelope()
        prompt = _build_llm_prompt(e)
        assert "github.com/test/repo" in prompt

    def test_prompt_includes_ewu(self):
        e = _make_envelope()
        prompt = _build_llm_prompt(e)
        assert "EWU" in prompt

    def test_prompt_with_pr_lifecycle(self):
        e = _make_envelope(
            signal_context={
                "evidence_count": 1,
                "repo_url": "https://github.com/test/repo",
                "pr_url": "https://github.com/test/repo/pull/1",
                "pr_lifecycle": {"pr_status": "merged"},
                "signal_status": "strong",
            }
        )
        prompt = _build_llm_prompt(e)
        assert "merged" in prompt
        assert "strong" in prompt


class TestDualTrackFallback:
    """When LLM is disabled or fails, rule-based brief is returned."""

    @pytest.mark.asyncio
    async def test_llm_disabled_returns_rule_based(self):
        """With LLM disabled, should return rule-based brief."""
        e = _make_envelope()
        c = _make_contract(e)
        with patch("app.services.agents.review_prep_agent.LLM_ENABLED", False):
            r = await run_review_prep_agent(e, c)
        assert r.structured_payload["brief_source"] == "rule_based"

    @pytest.mark.asyncio
    async def test_llm_failure_falls_back(self):
        """When LLM call fails, should fall back to rule-based."""
        e = _make_envelope()
        c = _make_contract(e)
        with (
            patch("app.services.agents.review_prep_agent.LLM_ENABLED", True),
            patch(
                "app.services.agents.review_prep_agent._try_llm_brief",
                new_callable=AsyncMock,
                return_value=None,
            ),
        ):
            r = await run_review_prep_agent(e, c)
        assert r.structured_payload["brief_source"] == "rule_based"

    @pytest.mark.asyncio
    async def test_llm_success_returns_llm_brief(self):
        """When LLM succeeds, should return LLM brief with source marker."""
        llm_output = {
            "task_summary": "Auth module implementation review",
            "completion_criteria_analysis": "Tests pass criteria appears covered",
            "evidence_summary": "2 evidence items submitted including code PR",
            "signal_summary": "Repository linked with active signals",
            "gaps_and_risks": ["No documentation evidence found"],
            "reviewer_focus_areas": ["Verify test coverage claim"],
            "uncertainty_note": "Evidence coverage assessment is AI-inferred",
        }
        e = _make_envelope()
        c = _make_contract(e)
        with (
            patch("app.services.agents.review_prep_agent.LLM_ENABLED", True),
            patch(
                "app.services.agents.review_prep_agent._try_llm_brief",
                new_callable=AsyncMock,
                return_value=llm_output,
            ),
        ):
            r = await run_review_prep_agent(e, c)
        assert r.structured_payload["brief_source"] == "llm"
        assert r.structured_payload["task_summary"] == "Auth module implementation review"
        assert "No documentation evidence found" in r.structured_payload["gaps_and_risks"]
        assert r.confidence == 0.75  # capped for LLM
        assert r.requires_human_review is True
        # Rule-based metadata preserved
        assert "review_checklist" in r.structured_payload
        assert r.structured_payload["evidence_count"] == 2


class TestLLMBriefSafety:
    """Verify LLM brief doesn't contain decision language."""

    @pytest.mark.asyncio
    async def test_llm_brief_always_requires_human_review(self):
        llm_output = {
            "task_summary": "Summary",
            "completion_criteria_analysis": "Analysis",
            "evidence_summary": "Evidence",
            "signal_summary": "Signals",
            "gaps_and_risks": [],
            "reviewer_focus_areas": [],
            "uncertainty_note": "Note",
        }
        e = _make_envelope()
        c = _make_contract(e)
        with (
            patch("app.services.agents.review_prep_agent.LLM_ENABLED", True),
            patch(
                "app.services.agents.review_prep_agent._try_llm_brief",
                new_callable=AsyncMock,
                return_value=llm_output,
            ),
        ):
            r = await run_review_prep_agent(e, c)
        assert r.requires_human_review is True
        # Confidence capped below rule-based maximum
        assert r.confidence <= 0.75

    def test_system_prompt_contains_safety_rules(self):
        from app.services.agents.review_prep_agent import REVIEW_SYSTEM_PROMPT

        assert "MUST NOT make approve/reject" in REVIEW_SYSTEM_PROMPT
        assert "MUST NOT claim evidence exists" in REVIEW_SYSTEM_PROMPT
        assert "human reviewer makes all decisions" in REVIEW_SYSTEM_PROMPT


class TestLLMClient:
    """Test the thin LLM client."""

    @pytest.mark.asyncio
    async def test_no_api_key_returns_none(self):
        from app.services.agents.llm_client import generate_structured

        with patch("app.services.agents.llm_client.ANTHROPIC_API_KEY", ""):
            result = await generate_structured("system", "user")
        assert result is None
