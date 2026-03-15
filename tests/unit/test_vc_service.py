"""Unit tests for VerifiableCredential service logic."""

import pytest
from pydantic import ValidationError

from shared_events import Subjects

from app.schemas.credential import IssueCredentialRequest, VerifyResponse
from app.services.vc_service import VALID_CREDENTIAL_TYPES


class TestCredentialTypes:
    def test_task_completion_is_valid(self) -> None:
        assert "task_completion" in VALID_CREDENTIAL_TYPES

    def test_project_participation_is_valid(self) -> None:
        assert "project_participation" in VALID_CREDENTIAL_TYPES

    def test_unknown_type_is_invalid(self) -> None:
        assert "fake_type" not in VALID_CREDENTIAL_TYPES

    def test_exactly_two_types(self) -> None:
        assert len(VALID_CREDENTIAL_TYPES) == 2


class TestCredentialTypeSchemaValidation:
    """I-5: credential_type must be Literal, not arbitrary str."""

    def test_valid_task_completion_accepted(self) -> None:
        import uuid

        req = IssueCredentialRequest(
            actor_id=uuid.uuid4(),
            credential_type="task_completion",
        )
        assert req.credential_type == "task_completion"

    def test_valid_project_participation_accepted(self) -> None:
        import uuid

        req = IssueCredentialRequest(
            actor_id=uuid.uuid4(),
            credential_type="project_participation",
        )
        assert req.credential_type == "project_participation"

    def test_invalid_credential_type_rejected(self) -> None:
        import uuid

        with pytest.raises(ValidationError):
            IssueCredentialRequest(
                actor_id=uuid.uuid4(),
                credential_type="fake_type",
            )

    def test_empty_credential_type_rejected(self) -> None:
        import uuid

        with pytest.raises(ValidationError):
            IssueCredentialRequest(
                actor_id=uuid.uuid4(),
                credential_type="",
            )

    def test_extra_fields_rejected(self) -> None:
        import uuid

        with pytest.raises(ValidationError, match="extra_forbidden"):
            IssueCredentialRequest(
                actor_id=uuid.uuid4(),
                credential_type="task_completion",
                unknown_field="value",
            )


class TestVerifyResponseMinimalFields:
    """I-3: VerifyResponse must not contain internal IDs or full credential data."""

    def test_valid_response_has_minimal_fields(self) -> None:
        from datetime import UTC, datetime

        resp = VerifyResponse(
            valid=True,
            credential_type="task_completion",
            issued_at=datetime.now(UTC),
        )
        data = resp.model_dump()
        assert set(data.keys()) == {"valid", "credential_type", "issued_at"}

    def test_invalid_response_has_no_credential_details(self) -> None:
        resp = VerifyResponse(valid=False)
        data = resp.model_dump()
        assert "actor_id" not in data
        assert "project_id" not in data
        assert "credential_data" not in data
        assert data["credential_type"] is None
        assert data["issued_at"] is None

    def test_verify_response_does_not_have_actor_id_field(self) -> None:
        assert "actor_id" not in VerifyResponse.model_fields

    def test_verify_response_does_not_have_credential_data_field(self) -> None:
        assert "credential_data" not in VerifyResponse.model_fields


class TestCredentialNATSSubjects:
    """B-3: NATS subjects must exist for credential events."""

    def test_credential_issued_subject_exists(self) -> None:
        assert hasattr(Subjects, "CREDENTIAL_ISSUED")

    def test_credential_issued_follows_naming_convention(self) -> None:
        parts = Subjects.CREDENTIAL_ISSUED.split(".")
        assert len(parts) == 3, "Subject must follow domain.entity.action format"
        assert parts[0] == "credential"
        assert parts[2] == "issued"
