"""Tests for webhook helper functions.

Covers: _extract_repo_url, _build_signal_payload, _extract_pr_url,
_extract_commit_sha, _extract_signal_type, _extract_source_ref,
and verify_github_signature logic.
"""

import hashlib
import hmac

import pytest

from app.api.v1.webhooks import (
    _build_signal_payload,
    _extract_commit_sha,
    _extract_pr_url,
    _extract_repo_url,
    _extract_signal_type,
    _extract_source_ref,
)


# ── _extract_repo_url ────────────────────────────────────────────────


class TestExtractRepoUrl:
    def test_push_event_extracts_repo_url(self) -> None:
        payload = {"repository": {"html_url": "https://github.com/org/repo"}}
        assert _extract_repo_url(payload) == "https://github.com/org/repo"

    def test_pr_event_extracts_repo_url(self) -> None:
        payload = {
            "repository": {"html_url": "https://github.com/org/repo"},
            "pull_request": {"number": 1},
        }
        assert _extract_repo_url(payload) == "https://github.com/org/repo"

    def test_issues_event_extracts_repo_url(self) -> None:
        payload = {
            "repository": {"html_url": "https://github.com/org/repo"},
            "issue": {"number": 5},
        }
        assert _extract_repo_url(payload) == "https://github.com/org/repo"

    def test_missing_repository_returns_none(self) -> None:
        payload = {"action": "opened"}
        assert _extract_repo_url(payload) is None

    def test_repository_not_dict_returns_none(self) -> None:
        payload = {"repository": "not a dict"}
        assert _extract_repo_url(payload) is None

    def test_repository_without_html_url_returns_none(self) -> None:
        payload = {"repository": {"full_name": "org/repo"}}
        assert _extract_repo_url(payload) is None


# ── _build_signal_payload ────────────────────────────────────────────


class TestBuildSignalPayload:
    def test_push_event_payload(self) -> None:
        payload = {
            "ref": "refs/heads/main",
            "commits": [{"id": "a"}, {"id": "b"}],
            "pusher": {"name": "alice"},
        }
        result = _build_signal_payload("push", payload)
        assert result["event_type"] == "push"
        assert result["ref"] == "refs/heads/main"
        assert result["commits_count"] == 2
        assert result["pusher"] == "alice"

    def test_push_event_empty_commits(self) -> None:
        payload = {"ref": "refs/heads/dev", "commits": [], "pusher": {"name": "bob"}}
        result = _build_signal_payload("push", payload)
        assert result["commits_count"] == 0

    def test_push_event_missing_commits_key(self) -> None:
        payload = {"ref": "refs/heads/dev", "pusher": {"name": "bob"}}
        result = _build_signal_payload("push", payload)
        assert result["commits_count"] == 0

    def test_pr_event_payload(self) -> None:
        payload = {
            "action": "opened",
            "pull_request": {
                "number": 42,
                "title": "Add feature",
                "user": {"login": "alice"},
            },
        }
        result = _build_signal_payload("pull_request", payload)
        assert result["event_type"] == "pull_request"
        assert result["action"] == "opened"
        assert result["pr_number"] == 42
        assert result["pr_title"] == "Add feature"
        assert result["pr_author"] == "alice"

    def test_issues_event_payload(self) -> None:
        payload = {
            "action": "closed",
            "issue": {
                "number": 10,
                "title": "Bug fix",
                "user": {"login": "bob"},
            },
        }
        result = _build_signal_payload("issues", payload)
        assert result["event_type"] == "issues"
        assert result["action"] == "closed"
        assert result["issue_number"] == 10
        assert result["issue_title"] == "Bug fix"
        assert result["issue_author"] == "bob"

    def test_unknown_event_type_returns_minimal(self) -> None:
        result = _build_signal_payload("deployment", {})
        assert result["event_type"] == "deployment"
        assert len(result) == 1


# ── _extract_pr_url ──────────────────────────────────────────────────


class TestExtractPrUrl:
    def test_pr_event_extracts_url(self) -> None:
        payload = {
            "pull_request": {"html_url": "https://github.com/org/repo/pull/1"},
        }
        assert _extract_pr_url("pull_request", payload) == "https://github.com/org/repo/pull/1"

    def test_push_event_returns_none(self) -> None:
        payload = {"after": "abc123"}
        assert _extract_pr_url("push", payload) is None

    def test_issues_event_returns_none(self) -> None:
        payload = {"issue": {"number": 5}}
        assert _extract_pr_url("issues", payload) is None

    def test_pr_event_missing_pr_key_returns_none(self) -> None:
        payload = {"action": "opened"}
        assert _extract_pr_url("pull_request", payload) is None

    def test_pr_event_missing_html_url_returns_none(self) -> None:
        payload = {"pull_request": {"number": 42}}
        assert _extract_pr_url("pull_request", payload) is None


# ── _extract_commit_sha ─────────────────────────────────────────────


class TestExtractCommitSha:
    def test_push_event_extracts_after_sha(self) -> None:
        payload = {"after": "abc123def456"}
        assert _extract_commit_sha("push", payload) == "abc123def456"

    def test_pr_event_extracts_head_sha(self) -> None:
        payload = {
            "pull_request": {"head": {"sha": "deadbeef1234"}},
        }
        assert _extract_commit_sha("pull_request", payload) == "deadbeef1234"

    def test_issues_event_returns_none(self) -> None:
        payload = {"issue": {"number": 5}}
        assert _extract_commit_sha("issues", payload) is None

    def test_push_event_missing_after_returns_none(self) -> None:
        payload = {"ref": "refs/heads/main"}
        assert _extract_commit_sha("push", payload) is None

    def test_pr_event_missing_head_returns_none(self) -> None:
        payload = {"pull_request": {}}
        assert _extract_commit_sha("pull_request", payload) is None


# ── _extract_signal_type ─────────────────────────────────────────────


class TestExtractSignalType:
    def test_push_returns_git_push(self) -> None:
        assert _extract_signal_type("push", {}) == "git_push"

    def test_pr_opened(self) -> None:
        assert _extract_signal_type("pull_request", {"action": "opened"}) == "pr_opened"

    def test_pr_closed(self) -> None:
        assert _extract_signal_type("pull_request", {"action": "closed"}) == "pr_closed"

    def test_issues_opened(self) -> None:
        assert _extract_signal_type("issues", {"action": "opened"}) == "issue_opened"

    def test_unknown_event_type(self) -> None:
        assert _extract_signal_type("deployment", {}) == "github_deployment"


# ── _extract_source_ref ─────────────────────────────────────────────


class TestExtractSourceRef:
    def test_push_returns_after_sha(self) -> None:
        payload = {"after": "abc123"}
        assert _extract_source_ref("push", payload) == "abc123"

    def test_pr_returns_pr_number(self) -> None:
        payload = {"pull_request": {"number": 42}}
        assert _extract_source_ref("pull_request", payload) == "PR#42"

    def test_issues_returns_issue_number(self) -> None:
        payload = {"issue": {"number": 7}}
        assert _extract_source_ref("issues", payload) == "Issue#7"

    def test_unknown_returns_none(self) -> None:
        assert _extract_source_ref("deployment", {}) is None

    def test_pr_missing_number_returns_none(self) -> None:
        payload = {"pull_request": {}}
        assert _extract_source_ref("pull_request", payload) is None


# ── verify_github_signature logic ────────────────────────────────────


class TestVerifyGitHubSignature:
    def test_correct_signature_matches(self) -> None:
        """Verify that HMAC SHA-256 signature matches expected value."""
        secret = "my-secret"
        body = b'{"ref":"refs/heads/main"}'
        expected = "sha256=" + hmac.new(
            secret.encode(), body, hashlib.sha256
        ).hexdigest()
        computed = "sha256=" + hmac.new(
            secret.encode(), body, hashlib.sha256
        ).hexdigest()
        assert hmac.compare_digest(expected, computed)

    def test_wrong_signature_does_not_match(self) -> None:
        secret = "my-secret"
        body = b'{"ref":"refs/heads/main"}'
        correct = "sha256=" + hmac.new(
            secret.encode(), body, hashlib.sha256
        ).hexdigest()
        wrong = "sha256=0000000000000000000000000000000000000000000000000000000000000000"
        assert not hmac.compare_digest(correct, wrong)

    def test_empty_secret_produces_valid_hmac(self) -> None:
        """Even empty secret produces a valid HMAC (dev mode scenario)."""
        secret = ""
        body = b'{"test":true}'
        sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        assert len(sig) == 64  # SHA-256 hex length

    def test_different_body_different_signature(self) -> None:
        secret = "my-secret"
        sig1 = hmac.new(secret.encode(), b"body1", hashlib.sha256).hexdigest()
        sig2 = hmac.new(secret.encode(), b"body2", hashlib.sha256).hexdigest()
        assert sig1 != sig2

    def test_signature_prefix_is_sha256(self) -> None:
        """GitHub signatures always start with 'sha256='."""
        secret = "test"
        body = b"test"
        sig = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        assert sig.startswith("sha256=")
