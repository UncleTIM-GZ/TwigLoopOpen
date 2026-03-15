"""Custom assertion helpers for Twig Loop tests."""

from __future__ import annotations

from typing import Any


def assert_violation(violations: list[Any], rule_code: str) -> None:
    """Assert that the given rule_code appears in a list of violation objects.

    Each violation is expected to have a `.rule_code` attribute.
    """
    codes = [v.rule_code for v in violations]
    assert rule_code in codes, f"Expected {rule_code!r} in {codes}"


def assert_no_violations(violations: list[Any]) -> None:
    """Assert that the violations list is empty."""
    assert len(violations) == 0, (
        f"Expected no violations, got {[v.rule_code for v in violations]}"
    )


def assert_api_success(response_json: dict[str, Any]) -> dict[str, Any]:
    """Assert the standard API envelope indicates success and return 'data'."""
    assert response_json["success"] is True, f"API error: {response_json.get('error')}"
    return response_json["data"]


def assert_api_error(response_json: dict[str, Any], *, expected_fragment: str | None = None) -> str:
    """Assert the standard API envelope indicates failure and return 'error'."""
    assert response_json["success"] is False, "Expected API failure but got success"
    error_msg = response_json["error"]
    if expected_fragment:
        assert expected_fragment in error_msg, (
            f"Expected {expected_fragment!r} in error message {error_msg!r}"
        )
    return error_msg


def assert_status_code(response, expected: int) -> None:
    """Assert HTTP response status code."""
    assert response.status_code == expected, (
        f"Expected status {expected}, got {response.status_code}: {response.text}"
    )
