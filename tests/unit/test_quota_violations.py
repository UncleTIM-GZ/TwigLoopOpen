"""Tests for QuotaViolation dataclass."""

from app.services.quota_preflight_service import QuotaViolation


class TestQuotaViolationFields:
    def test_all_seven_fields_present(self) -> None:
        v = QuotaViolation(
            rule_code="WP_PER_PROJECT",
            severity="error",
            object_scope="project",
            current_value=6,
            max_allowed=5,
            message="Too many work packages",
            recommended_next_action="Merge related work packages",
        )
        assert v.rule_code == "WP_PER_PROJECT"
        assert v.severity == "error"
        assert v.object_scope == "project"
        assert v.current_value == 6
        assert v.max_allowed == 5
        assert v.message == "Too many work packages"
        assert v.recommended_next_action == "Merge related work packages"

    def test_severity_warning(self) -> None:
        v = QuotaViolation(
            rule_code="OPEN_SEATS",
            severity="warning",
            object_scope="founder",
            current_value=13,
            max_allowed=12,
            message="Too many open seats",
            recommended_next_action="Fill or close existing seats",
        )
        assert v.severity == "warning"

    def test_float_current_value(self) -> None:
        v = QuotaViolation(
            rule_code="EWU_PER_TASK",
            severity="error",
            object_scope="task:My Task",
            current_value=9.5,
            max_allowed=8,
            message="EWU too high",
            recommended_next_action="Reduce scope",
        )
        assert v.current_value == 9.5


class TestQuotaViolationToDict:
    def test_to_dict_returns_all_keys(self) -> None:
        v = QuotaViolation(
            rule_code="WP_PER_PROJECT",
            severity="error",
            object_scope="project",
            current_value=6,
            max_allowed=5,
            message="Too many work packages",
            recommended_next_action="Merge related work packages",
        )
        d = v.to_dict()
        assert isinstance(d, dict)
        assert set(d.keys()) == {
            "rule_code",
            "severity",
            "object_scope",
            "current_value",
            "max_allowed",
            "message",
            "recommended_next_action",
        }

    def test_to_dict_values_match(self) -> None:
        v = QuotaViolation(
            rule_code="EWU_PER_TASK",
            severity="error",
            object_scope="task:Build API",
            current_value=9,
            max_allowed=8,
            message="EWU too high",
            recommended_next_action="Split task",
        )
        d = v.to_dict()
        assert d["rule_code"] == "EWU_PER_TASK"
        assert d["severity"] == "error"
        assert d["object_scope"] == "task:Build API"
        assert d["current_value"] == 9
        assert d["max_allowed"] == 8
        assert d["message"] == "EWU too high"
        assert d["recommended_next_action"] == "Split task"

    def test_to_dict_returns_plain_dict(self) -> None:
        v = QuotaViolation(
            rule_code="TASKS_PER_WP",
            severity="error",
            object_scope="work_package:Phase 1",
            current_value=7,
            max_allowed=6,
            message="Too many tasks",
            recommended_next_action="Split WP",
        )
        d = v.to_dict()
        assert type(d) is dict
