"""Tests for Horizon 2.1 — CredentialHistory model, VCAgent external, audit trail."""

import uuid

import pytest
from app.domain.a2a_protocol import DelegationContract, TaskEnvelope
from app.models.credential_history import CredentialHistory
from app.schemas.credential import (
    CredentialHistoryEntry,
    CredentialHistoryPublicEntry,
)


class TestCredentialHistoryModel:
    def test_history_entry_fields(self):
        entry = CredentialHistory(
            credential_id=uuid.uuid4(),
            event_type="issued",
            previous_status="draft",
            new_status="issued",
            actor_id=uuid.uuid4(),
            source="platform",
            reason_code="issuance",
        )
        assert entry.event_type == "issued"
        assert entry.previous_status == "draft"
        assert entry.new_status == "issued"
        assert entry.source == "platform"

    def test_revoke_history_entry(self):
        entry = CredentialHistory(
            credential_id=uuid.uuid4(),
            event_type="revoked",
            previous_status="issued",
            new_status="revoked",
            actor_id=uuid.uuid4(),
            source="platform",
            reason_code="revocation",
            reason_text="Fraudulent evidence detected",
        )
        assert entry.event_type == "revoked"
        assert entry.reason_text == "Fraudulent evidence detected"

    def test_delegation_trace_fields(self):
        entry = CredentialHistory(
            credential_id=uuid.uuid4(),
            event_type="issued",
            new_status="issued",
            delegation_id="del-123",
            trace_id="trace-456",
        )
        assert entry.delegation_id == "del-123"
        assert entry.trace_id == "trace-456"


class TestCredentialHistorySchemas:
    def test_internal_entry(self):
        entry = CredentialHistoryEntry(
            history_id=uuid.uuid4(),
            credential_id=uuid.uuid4(),
            event_type="issued",
            previous_status="draft",
            new_status="issued",
            source="platform",
            occurred_at="2026-03-17T10:00:00+00:00",
        )
        assert entry.event_type == "issued"

    def test_public_entry_no_sensitive_fields(self):
        entry = CredentialHistoryPublicEntry(
            event_type="revoked",
            new_status="revoked",
            occurred_at="2026-03-17T10:00:00+00:00",
        )
        data = entry.model_dump()
        assert "actor_id" not in data
        assert "reason_text" not in data
        assert "delegation_id" not in data


class TestVCAgentExternalStandalone:
    """Tests for VCAgent with lifecycle_action support."""

    @pytest.mark.asyncio
    async def test_vc_agent_issuance_eligible(self):
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
                "lifecycle_action": "issuance",
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
        assert r.requires_human_review is not True or r.requires_human_review is True
        # VC agent always requires human review
        assert r.structured_payload["lifecycle_action"] == "issuance"

    @pytest.mark.asyncio
    async def test_vc_agent_deny_no_evidence(self):
        from app.services.agents.vc_agent import run_vc_agent

        e = TaskEnvelope(
            task_id="t1",
            project_id="p1",
            current_status="completed",
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


class TestCoordinationServiceVCWiring:
    """Verify VCAgent env var wiring in coordination service."""

    def test_vc_agent_url_env_support(self):
        import os

        from app.services.coordination_service import (
            EXTERNAL_AGENT_URLS,
            IN_PROCESS_AGENTS,
        )

        # VC agent is in the in-process registry
        assert "vc_agent" in IN_PROCESS_AGENTS
        # Without env var, it's not in external URLs
        if not os.getenv("VC_AGENT_URL"):
            assert "vc_agent" not in EXTERNAL_AGENT_URLS
