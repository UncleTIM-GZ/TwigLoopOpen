"""GitHub Signal Agent — normalizes GitHub data into platform signals.

In-process version (also serves as fallback when external agent is unavailable).
H2: enhanced with PR lifecycle tracking and signal quality tiers.
"""

from app.domain.a2a_protocol import AgentResult, DelegationContract, TaskEnvelope

AGENT_VERSION = "2.0.0"


async def run_github_signal_agent(
    envelope: TaskEnvelope, contract: DelegationContract
) -> AgentResult:
    """Normalize GitHub signal inputs into a platform signal snapshot."""
    repo_url = envelope.signal_context.get("repo_url", "")
    pr_url = envelope.signal_context.get("pr_url", "")
    commit_sha = envelope.signal_context.get("latest_commit_sha", "")
    branch = envelope.signal_context.get("branch_name", "")

    # H2: PR lifecycle data from webhook events
    pr_state = envelope.signal_context.get("pr_state", "")
    pr_merged = envelope.signal_context.get("pr_merged", False)
    review_state = envelope.signal_context.get("review_state", "")
    commit_count = envelope.signal_context.get("commit_count", 0)

    signals: list[str] = []
    signal_count = 0

    if repo_url:
        signals.append(f"Repository linked: {repo_url}")
        signal_count += 1

    if branch:
        signals.append(f"Branch: {branch}")
        signal_count += 1

    if pr_url:
        signals.append(f"Pull request: {pr_url}")
        signal_count += 1
        if "/pull/" in pr_url:
            signals.append("PR appears to be a standard GitHub pull request")

    if commit_sha:
        signals.append(f"Latest commit: {commit_sha[:8]}...")
        signal_count += 1

    # H2: PR lifecycle signals
    pr_lifecycle = _analyze_pr_lifecycle(pr_state, pr_merged, review_state)
    if pr_lifecycle["pr_status"] != "unknown":
        signals.append(f"PR status: {pr_lifecycle['pr_status']}")
        if pr_lifecycle["pr_status"] in ("merged", "approved"):
            signal_count += 1

    if commit_count > 0:
        signals.append(f"Total commits: {commit_count}")

    # Determine signal quality tier
    status = _determine_signal_tier(signal_count, pr_lifecycle)

    if signal_count == 0:
        summary = "No GitHub signals available for this task."
    elif status == "strong":
        summary = "Strong GitHub signals — PR merged or approved with commit history."
    elif status == "active":
        summary = "GitHub signals present — repo, branch, and PR/commit available."
    elif status == "partial":
        summary = "Partial GitHub signal — repo or branch linked but no PR/commit yet."
    else:
        summary = "Minimal GitHub signal."

    return AgentResult(
        delegation_id=contract.delegation_id,
        result_type="signal_snapshot",
        summary=summary,
        structured_payload={
            "signal_status": status,
            "signal_count": signal_count,
            "signals": signals,
            "repo_url": repo_url,
            "branch_name": branch,
            "pr_url": pr_url,
            "latest_commit_sha": commit_sha,
            "normalized_status": status,
            "pr_lifecycle": pr_lifecycle,
            "commit_count": commit_count,
        },
        confidence=_calculate_confidence(signal_count, pr_lifecycle),
        requires_human_review=False,
        agent_version=AGENT_VERSION,
        trace_id=envelope.trace_id,
    )


def _analyze_pr_lifecycle(
    pr_state: str, pr_merged: bool, review_state: str
) -> dict[str, str | bool]:
    """Analyze PR lifecycle from webhook data."""
    if pr_merged or pr_state == "merged":
        pr_status = "merged"
    elif pr_state == "closed":
        pr_status = "closed"
    elif review_state == "approved":
        pr_status = "approved"
    elif review_state == "changes_requested":
        pr_status = "changes_requested"
    elif pr_state == "open":
        pr_status = "open"
    elif pr_state:
        pr_status = pr_state
    else:
        pr_status = "unknown"

    return {
        "pr_status": pr_status,
        "pr_merged": pr_merged,
        "review_state": review_state or "none",
    }


def _determine_signal_tier(signal_count: int, pr_lifecycle: dict[str, str | bool]) -> str:
    """Determine signal quality tier."""
    pr_status = pr_lifecycle.get("pr_status", "unknown")
    if pr_status in ("merged", "approved") and signal_count >= 3:
        return "strong"
    if signal_count >= 3:
        return "active"
    if signal_count >= 1:
        return "partial"
    return "no_signal"


def _calculate_confidence(signal_count: int, pr_lifecycle: dict[str, str | bool]) -> float:
    """Calculate confidence score based on signal quality."""
    pr_status = pr_lifecycle.get("pr_status", "unknown")
    if pr_status == "merged":
        return 0.95
    if pr_status == "approved":
        return 0.9
    if signal_count >= 3:
        return 0.8
    if signal_count >= 1:
        return 0.5
    return 0.1
