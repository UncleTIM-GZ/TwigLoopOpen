"""Tests for H3.1-b — Brief Persistence & Visibility."""

import uuid

from app.models.agent_brief import AgentBrief


class TestAgentBriefModel:
    def test_matching_brief_fields(self):
        brief = AgentBrief(
            task_id=uuid.uuid4(),
            brief_type="matching_brief",
            brief_source="llm",
            brief_version=1,
            status="active",
            content_json={
                "brief_source": "llm",
                "task_fit_summary": "Strong fit",
                "strengths": ["Python", "FastAPI"],
                "gaps_and_risks": ["No mobile experience"],
                "recommended_track": "formal_seat_candidate",
                "explanation": "Good match for backend work",
                "uncertainty_note": "Skills based on stated profile",
            },
        )
        assert brief.brief_type == "matching_brief"
        assert brief.brief_source == "llm"
        assert brief.content_json["task_fit_summary"] == "Strong fit"

    def test_review_brief_fields(self):
        brief = AgentBrief(
            task_id=uuid.uuid4(),
            brief_type="review_brief",
            brief_source="rule_based",
            brief_version=1,
            status="active",
            content_json={
                "brief_source": "rule_based",
                "task_summary": "Build auth module",
                "review_checklist": ["Check tests", "Check docs"],
                "evidence_count": 2,
            },
        )
        assert brief.brief_type == "review_brief"
        assert brief.brief_source == "rule_based"
        assert brief.content_json["evidence_count"] == 2

    def test_superseded_status(self):
        brief = AgentBrief(
            task_id=uuid.uuid4(),
            brief_type="matching_brief",
            brief_source="rule_based",
            brief_version=1,
            status="superseded",
            content_json={},
        )
        assert brief.status == "superseded"

    def test_version_increment(self):
        brief_v1 = AgentBrief(
            task_id=uuid.uuid4(),
            brief_type="review_brief",
            brief_source="rule_based",
            brief_version=1,
            content_json={},
        )
        brief_v2 = AgentBrief(
            task_id=brief_v1.task_id,
            brief_type="review_brief",
            brief_source="llm",
            brief_version=2,
            content_json={"task_summary": "Updated"},
        )
        assert brief_v2.brief_version > brief_v1.brief_version
        assert brief_v2.brief_source == "llm"


class TestAgentBriefModelColumns:
    def test_table_has_required_columns(self):
        columns = {c.name for c in AgentBrief.__table__.columns}
        assert "task_id" in columns
        assert "brief_type" in columns
        assert "brief_source" in columns
        assert "brief_version" in columns
        assert "status" in columns
        assert "content_json" in columns
        assert "actor_id" in columns
        assert "delegation_id" in columns
        assert "trace_id" in columns
        assert "created_at" in columns


class TestBriefServiceInterface:
    def test_brief_service_has_required_methods(self):

        from app.services.brief_service import BriefService

        methods = [m for m in dir(BriefService) if not m.startswith("_")]
        assert "save_brief" in methods
        assert "get_latest" in methods
        assert "get_history" in methods

    def test_save_brief_signature(self):
        import inspect

        from app.services.brief_service import BriefService

        sig = inspect.signature(BriefService.save_brief)
        params = list(sig.parameters.keys())
        assert "task_id" in params
        assert "brief_type" in params
        assert "brief_source" in params
        assert "content" in params
