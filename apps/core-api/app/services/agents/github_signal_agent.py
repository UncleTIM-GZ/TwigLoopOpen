"""GitHub Signal Agent — normalizes GitHub data into platform signals.

Phase 4.1: rule-based signal normalization, no GitHub API calls.
Accepts manually submitted repo/PR/commit info and produces signal snapshot.
"""

from app.domain.a2a_protocol import AgentResult, DelegationContract, TaskEnvelope


async def run_github_signal_agent(
    envelope: TaskEnvelope, contract: DelegationContract
) -> AgentResult:
    """Normalize GitHub signal inputs into a platform signal snapshot."""
    repo_url = envelope.signal_context.get("repo_url", "")
    pr_url = envelope.signal_context.get("pr_url", "")
    commit_sha = envelope.signal_context.get("latest_commit_sha", "")
    branch = envelope.signal_context.get("branch_name", "")

    signals = []
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
        # Infer PR status from URL pattern
        if "/pull/" in pr_url:
            signals.append("PR appears to be a standard GitHub pull request")

    if commit_sha:
        signals.append(f"Latest commit: {commit_sha[:8]}...")
        signal_count += 1

    if signal_count == 0:
        summary = "No GitHub signals available for this task."
        status = "no_signal"
    elif signal_count <= 2:
        summary = "Partial GitHub signal — repo or branch linked but no PR/commit yet."
        status = "partial"
    else:
        summary = "GitHub signals present — repo, branch, and PR/commit available."
        status = "active"

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
        },
        confidence=0.8 if signal_count >= 3 else 0.5 if signal_count >= 1 else 0.1,
        requires_human_review=False,
    )
