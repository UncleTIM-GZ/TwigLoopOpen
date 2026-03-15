"""Webhook routes — receive external platform events."""

import hashlib
import hmac
import logging
import os
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Request
from shared_events import Subjects, publish_event
from shared_schemas import ApiResponse

from app.db.session import async_session_factory
from app.services.signal_service import SignalService
from app.services.source_service import SourceService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
_logger = logging.getLogger(__name__)

# GitHub webhook secret for signature verification
# Set GITHUB_WEBHOOK_SECRET env var in production
_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")

# GitHub event types we handle
_SUPPORTED_EVENTS = {"push", "pull_request", "issues"}


def _extract_repo_url(payload: dict) -> str | None:  # type: ignore[type-arg]
    """Extract the repo HTML URL from a GitHub webhook payload."""
    repo = payload.get("repository")
    if repo and isinstance(repo, dict):
        return repo.get("html_url")  # type: ignore[no-any-return]
    return None


def _extract_signal_type(event_type: str, payload: dict) -> str:  # type: ignore[type-arg]
    """Map GitHub event to a signal_type string."""
    if event_type == "push":
        return "git_push"
    if event_type == "pull_request":
        action = payload.get("action", "unknown")
        return f"pr_{action}"
    if event_type == "issues":
        action = payload.get("action", "unknown")
        return f"issue_{action}"
    return f"github_{event_type}"


def _extract_source_ref(event_type: str, payload: dict) -> str | None:  # type: ignore[type-arg]
    """Extract a reference string (commit SHA, PR number, etc.)."""
    if event_type == "push":
        return payload.get("after")  # type: ignore[no-any-return]
    if event_type == "pull_request":
        pr = payload.get("pull_request", {})
        number = pr.get("number")
        return f"PR#{number}" if number else None
    if event_type == "issues":
        issue = payload.get("issue", {})
        number = issue.get("number")
        return f"Issue#{number}" if number else None
    return None


def _build_signal_payload(event_type: str, payload: dict) -> dict:  # type: ignore[type-arg]
    """Build a compact signal payload from the webhook data."""
    result: dict[str, object] = {"event_type": event_type}
    if event_type == "push":
        result["ref"] = payload.get("ref")
        result["commits_count"] = len(payload.get("commits", []))
        result["pusher"] = payload.get("pusher", {}).get("name")
    elif event_type == "pull_request":
        pr = payload.get("pull_request", {})
        result["action"] = payload.get("action")
        result["pr_number"] = pr.get("number")
        result["pr_title"] = pr.get("title")
        result["pr_author"] = pr.get("user", {}).get("login")
    elif event_type == "issues":
        issue = payload.get("issue", {})
        result["action"] = payload.get("action")
        result["issue_number"] = issue.get("number")
        result["issue_title"] = issue.get("title")
        result["issue_author"] = issue.get("user", {}).get("login")
    return result


async def _verify_github_signature(request: Request, body: bytes) -> None:
    """Verify GitHub webhook signature (X-Hub-Signature-256)."""
    if not _WEBHOOK_SECRET:
        return  # Skip verification if no secret configured (dev mode)
    signature_header = request.headers.get("X-Hub-Signature-256", "")
    if not signature_header:
        raise HTTPException(status_code=403, detail="Missing webhook signature")
    expected = (
        "sha256="
        + hmac.new(
            _WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
    )
    if not hmac.compare_digest(signature_header, expected):
        raise HTTPException(status_code=403, detail="Invalid webhook signature")


@router.post("/github")  # type: ignore[untyped-decorator]
async def github_webhook(request: Request) -> ApiResponse[dict[str, str]]:
    """Receive GitHub webhook events (push, PR, issue)."""
    body = await request.body()
    await _verify_github_signature(request, body)

    import json

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return ApiResponse(success=False, error="Invalid JSON payload")
    event_type = request.headers.get("X-GitHub-Event", "unknown")

    if event_type not in _SUPPORTED_EVENTS:
        return ApiResponse(success=True, data={"status": "ignored", "event": event_type})

    repo_url = _extract_repo_url(payload)
    if not repo_url:
        _logger.warning("GitHub webhook missing repository URL")
        return ApiResponse(success=True, data={"status": "ignored", "reason": "no_repo_url"})

    # Look up the project by repo URL
    async with async_session_factory() as session:
        try:
            source_svc = SourceService(session)
            source = await source_svc.find_project_by_repo_url(repo_url)
            if not source:
                _logger.info("No project bound to repo %s", repo_url)
                return ApiResponse(success=True, data={"status": "ignored", "reason": "no_binding"})

            signal_svc = SignalService(session)
            signal = await signal_svc.create_signal(
                project_id=source.project_id,
                signal_type=_extract_signal_type(event_type, payload),
                source_type="github",
                source_ref=_extract_source_ref(event_type, payload),
                payload=_build_signal_payload(event_type, payload),
                occurred_at=datetime.now(UTC),
            )
            await session.commit()
        except Exception:
            await session.rollback()
            _logger.exception("Failed to process GitHub webhook")
            raise

    # Also publish to NATS for source-sync-worker
    await publish_event(
        Subjects.SOURCE_WEBHOOK_RECEIVED,
        {
            "repo_url": repo_url,
            "event_type": event_type,
            "signal_id": str(signal.signal_id),
            "project_id": str(source.project_id),
        },
    )

    return ApiResponse(success=True, data={"status": "processed", "event": event_type})
