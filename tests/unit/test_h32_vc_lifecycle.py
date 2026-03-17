"""Tests for H3.2 — Complete VC Lifecycle (suspended, expired, transitions)."""

from app.services.vc_service import VALID_TRANSITIONS


class TestLifecycleTransitions:
    """Verify state machine rules."""

    def test_draft_can_issue(self):
        assert "issued" in VALID_TRANSITIONS["draft"]

    def test_issued_can_suspend(self):
        assert "suspended" in VALID_TRANSITIONS["issued"]

    def test_issued_can_revoke(self):
        assert "revoked" in VALID_TRANSITIONS["issued"]

    def test_issued_can_supersede(self):
        assert "superseded" in VALID_TRANSITIONS["issued"]

    def test_issued_can_expire(self):
        assert "expired" in VALID_TRANSITIONS["issued"]

    def test_suspended_can_reactivate(self):
        assert "issued" in VALID_TRANSITIONS["suspended"]

    def test_suspended_can_revoke(self):
        assert "revoked" in VALID_TRANSITIONS["suspended"]

    def test_suspended_cannot_supersede(self):
        assert "superseded" not in VALID_TRANSITIONS["suspended"]

    def test_revoked_is_terminal(self):
        assert len(VALID_TRANSITIONS["revoked"]) == 0

    def test_superseded_is_terminal(self):
        assert len(VALID_TRANSITIONS["superseded"]) == 0

    def test_expired_is_terminal(self):
        assert len(VALID_TRANSITIONS["expired"]) == 0

    def test_draft_cannot_revoke(self):
        assert "revoked" not in VALID_TRANSITIONS["draft"]

    def test_draft_cannot_suspend(self):
        assert "suspended" not in VALID_TRANSITIONS["draft"]


class TestLifecycleStates:
    """Verify all states are defined."""

    def test_all_states_present(self):
        expected = {"draft", "issued", "suspended", "revoked", "superseded", "expired"}
        assert set(VALID_TRANSITIONS.keys()) == expected


class TestCredentialModelFields:
    """Verify model has H3.2 fields."""

    def test_suspended_fields_exist(self):
        from app.models.verifiable_credential import VerifiableCredential

        # Check column exists on the model
        columns = {c.name for c in VerifiableCredential.__table__.columns}
        assert "suspended_at" in columns
        assert "suspension_reason" in columns
        assert "suspended_by" in columns
        assert "valid_until" in columns


class TestStatusResponseFields:
    """Verify status response includes H3.2 fields."""

    def test_status_response_has_new_fields(self):
        from app.schemas.credential import CredentialStatusResponse

        fields = set(CredentialStatusResponse.model_fields.keys())
        assert "valid_until" in fields
        assert "suspended_at" in fields


class TestSuspendSchema:
    """Verify suspend request schema."""

    def test_suspend_request(self):
        from app.schemas.credential import SuspendCredentialRequest

        req = SuspendCredentialRequest(reason="Evidence under review")
        assert req.reason == "Evidence under review"
