"""Tests for Horizon 2.3 — LLM-enhanced MatchingAgent dual-track."""

from unittest.mock import AsyncMock, patch

import pytest
from app.domain.a2a_protocol import DelegationContract, TaskEnvelope
from app.services.agents.matching_agent import (
    _build_llm_prompt,
    _build_rule_based_matching,
    run_matching_agent,
)


def _make_envelope(**overrides):
    defaults = {
        "task_id": "t1",
        "project_id": "p1",
        "objective": "Build payment integration module",
        "current_status": "open",
        "constraints": {
            "task_type": "development",
            "main_role": "backend_developer",
            "risk_level": "medium",
            "ewu": "7.0",
        },
    }
    defaults.update(overrides)
    return TaskEnvelope(**defaults)


def _make_contract(envelope):
    return DelegationContract(
        envelope_id=envelope.envelope_id,
        delegator_agent="coord",
        delegatee_agent="matching_agent",
        delegation_type="matching",
    )


class TestRuleBasedMatching:
    def test_development_high_ewu(self):
        e = _make_envelope()
        c = _make_contract(e)
        r = _build_rule_based_matching(e, c)
        assert r.structured_payload["brief_source"] == "rule_based"
        assert r.structured_payload["recommended_seat_type"] == "formal"
        assert r.structured_payload["complexity_level"] == "high"

    def test_low_ewu_growth(self):
        e = _make_envelope(
            constraints={"task_type": "development", "main_role": "dev", "ewu": "2.0"}
        )
        c = _make_contract(e)
        r = _build_rule_based_matching(e, c)
        assert r.structured_payload["recommended_seat_type"] == "growth"
        assert r.structured_payload["complexity_level"] == "low"

    def test_design_task(self):
        e = _make_envelope(
            constraints={"task_type": "product_design", "main_role": "designer", "ewu": "3.0"}
        )
        c = _make_contract(e)
        r = _build_rule_based_matching(e, c)
        assert "design" in r.summary.lower()

    def test_agent_version(self):
        e = _make_envelope()
        c = _make_contract(e)
        r = _build_rule_based_matching(e, c)
        assert r.agent_version == "2.3.0"

    def test_always_requires_human_review(self):
        e = _make_envelope()
        c = _make_contract(e)
        r = _build_rule_based_matching(e, c)
        assert r.requires_human_review is True


class TestLLMPromptBuilding:
    def test_prompt_includes_objective(self):
        e = _make_envelope()
        prompt = _build_llm_prompt(e)
        assert "Build payment integration module" in prompt

    def test_prompt_includes_task_type(self):
        e = _make_envelope()
        prompt = _build_llm_prompt(e)
        assert "development" in prompt

    def test_prompt_includes_ewu(self):
        e = _make_envelope()
        prompt = _build_llm_prompt(e)
        assert "7.0" in prompt

    def test_prompt_includes_candidate_context(self):
        e = _make_envelope(
            signal_context={
                "candidate_skills": "Python, FastAPI, PostgreSQL",
                "candidate_experience": "3 years backend",
                "application_note": "Interested in fintech projects",
            }
        )
        prompt = _build_llm_prompt(e)
        assert "Python, FastAPI" in prompt
        assert "3 years backend" in prompt
        assert "fintech" in prompt


class TestDualTrackFallback:
    @pytest.mark.asyncio
    async def test_llm_disabled_returns_rule_based(self):
        e = _make_envelope()
        c = _make_contract(e)
        with patch("app.services.agents.matching_agent.LLM_ENABLED", False):
            r = await run_matching_agent(e, c)
        assert r.structured_payload["brief_source"] == "rule_based"

    @pytest.mark.asyncio
    async def test_llm_failure_falls_back(self):
        e = _make_envelope()
        c = _make_contract(e)
        with (
            patch("app.services.agents.matching_agent.LLM_ENABLED", True),
            patch(
                "app.services.agents.matching_agent._try_llm_matching",
                new_callable=AsyncMock,
                return_value=None,
            ),
        ):
            r = await run_matching_agent(e, c)
        assert r.structured_payload["brief_source"] == "rule_based"

    @pytest.mark.asyncio
    async def test_llm_success_returns_llm_brief(self):
        llm_output = {
            "task_fit_summary": "Strong fit for backend payment work",
            "strengths": ["Python expertise", "Fintech interest"],
            "gaps_and_risks": ["No payment gateway experience mentioned"],
            "recommended_track": "formal_seat_candidate",
            "explanation": "Candidate has strong backend skills matching payment needs",
            "uncertainty_note": "Skills assessment based on stated profile only",
            "structured_signals": {
                "skill_overlap": "high",
                "complexity_fit": "medium",
                "collaboration_fit": "unknown",
            },
        }
        e = _make_envelope()
        c = _make_contract(e)
        with (
            patch("app.services.agents.matching_agent.LLM_ENABLED", True),
            patch(
                "app.services.agents.matching_agent._try_llm_matching",
                new_callable=AsyncMock,
                return_value=llm_output,
            ),
        ):
            r = await run_matching_agent(e, c)
        assert r.structured_payload["brief_source"] == "llm"
        assert r.structured_payload["recommended_track"] == "formal_seat_candidate"
        assert "Python expertise" in r.structured_payload["strengths"]
        assert r.requires_human_review is True
        # Rule-based metadata preserved
        assert "recommended_seat_type" in r.structured_payload
        assert "skill_requirements" in r.structured_payload


class TestMatchingSafety:
    def test_system_prompt_contains_safety_rules(self):
        from app.services.agents.matching_agent import MATCHING_SYSTEM_PROMPT

        assert "MUST NOT make accept/reject" in MATCHING_SYSTEM_PROMPT
        assert "MUST NOT claim skills" in MATCHING_SYSTEM_PROMPT
        assert "MUST NOT assign seats" in MATCHING_SYSTEM_PROMPT
        assert "human makes all decisions" in MATCHING_SYSTEM_PROMPT

    @pytest.mark.asyncio
    async def test_llm_brief_always_requires_human_review(self):
        llm_output = {
            "task_fit_summary": "Good fit",
            "strengths": [],
            "gaps_and_risks": [],
            "recommended_track": "formal_seat_candidate",
            "explanation": "Looks good",
            "uncertainty_note": "Note",
            "structured_signals": {},
        }
        e = _make_envelope()
        c = _make_contract(e)
        with (
            patch("app.services.agents.matching_agent.LLM_ENABLED", True),
            patch(
                "app.services.agents.matching_agent._try_llm_matching",
                new_callable=AsyncMock,
                return_value=llm_output,
            ),
        ):
            r = await run_matching_agent(e, c)
        assert r.requires_human_review is True
