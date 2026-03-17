"use client";

import { useState } from "react";
import Link from "next/link";
import { useMe } from "@/hooks/use-auth";
import { usePendingReviews, useSubmitReview } from "@/hooks/use-reviews";
import { useMyTasks } from "@/hooks/use-dashboard";

const VERIFICATION_COLORS: Record<string, string> = {
  unverified: "text-gray-500",
  pending: "text-yellow-400",
  verified: "text-green-400",
  rejected: "text-red-400",
};

const TASK_STATUS_COLORS: Record<string, string> = {
  submitted: "text-yellow-400",
  under_review: "text-cyan-400",
  in_progress: "text-blue-400",
  completed: "text-green-400",
};

export default function ReviewerDashboardPage() {
  const { data: meRes, isLoading: meLoading } = useMe();
  const { data: reviewsRes, isLoading: reviewsLoading } = usePendingReviews();
  const { data: tasksRes, isLoading: tasksLoading } = useMyTasks();

  if (meLoading) return <p className="text-muted-foreground">Loading...</p>;

  const actor = meRes?.data?.actor;
  if (!actor?.is_reviewer) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground mb-4">
          Only reviewer role can access this page
        </p>
        <Link href="/dashboard" className="underline">
          Back to Dashboard
        </Link>
      </div>
    );
  }

  const pendingItems = reviewsRes?.data ?? [];
  const allTasks = tasksRes?.data ?? [];
  const reviewableTasks = allTasks.filter(
    (t) => t.status === "submitted" || t.status === "under_review",
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold font-mono text-green-400">
          ~/dashboard/reviewer
        </h1>
        <Link href="/dashboard" className="text-sm underline">
          Back to Dashboard
        </Link>
      </div>

      {/* Existing: Pending Project Reviews (public benefit) */}
      <section className="mb-10">
        <h2 className="text-lg font-semibold mb-3">
          Pending Reviews ({pendingItems.length})
        </h2>
        {reviewsLoading ? (
          <p className="text-muted-foreground">Loading...</p>
        ) : pendingItems.length === 0 ? (
          <p className="text-muted-foreground">No pending reviews</p>
        ) : (
          <div className="grid gap-3">
            {pendingItems.map((item) => (
              <ReviewItem key={item.project_id} item={item} />
            ))}
          </div>
        )}
      </section>

      {/* New: Tasks Requiring Review */}
      <section>
        <h2 className="text-lg font-semibold mb-3 font-mono">
          Tasks Requiring Review ({reviewableTasks.length})
        </h2>
        {tasksLoading ? (
          <p className="text-muted-foreground">Loading...</p>
        ) : reviewableTasks.length === 0 ? (
          <p className="text-muted-foreground font-mono text-sm">
            No tasks awaiting review
          </p>
        ) : (
          <div className="grid gap-3">
            {reviewableTasks.map((task) => (
              <ReviewableTaskRow key={task.task_id} task={task} />
            ))}
          </div>
        )}
        <p className="text-xs text-gray-500 font-mono mt-3">
          Actions (approve / needs_revision / reject) are available via MCP
          tools.
        </p>
      </section>
    </div>
  );
}

function ReviewItem({
  item,
}: {
  item: { project_id: string; decision: string; created_at: string };
}) {
  const [feedback, setFeedback] = useState("");
  const [expanded, setExpanded] = useState(false);
  const submitMutation = useSubmitReview(item.project_id);

  const handleSubmit = (decision: "passed" | "needs_revision" | "rejected") => {
    submitMutation.mutate({
      decision,
      feedback: feedback || undefined,
    });
  };

  return (
    <div className="border rounded-lg p-4">
      <div className="flex justify-between items-center">
        <div>
          <Link
            href={`/projects/${item.project_id}`}
            className="font-medium hover:underline"
          >
            Project {item.project_id.slice(0, 8)}...
          </Link>
          <p className="text-xs text-muted-foreground">
            Created {new Date(item.created_at).toLocaleDateString("en-US")}
          </p>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-sm underline"
        >
          {expanded ? "Collapse" : "Review"}
        </button>
      </div>

      {expanded && (
        <div className="mt-3 space-y-3">
          <textarea
            className="w-full border rounded-lg p-2 text-sm"
            placeholder="Review feedback (optional)"
            rows={3}
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
          />
          <div className="flex gap-2">
            <button
              onClick={() => handleSubmit("passed")}
              disabled={submitMutation.isPending}
              className="rounded-lg bg-green-600 px-3 py-1.5 text-sm text-white hover:bg-green-700 disabled:opacity-50"
            >
              Approve
            </button>
            <button
              onClick={() => handleSubmit("needs_revision")}
              disabled={submitMutation.isPending}
              className="rounded-lg bg-yellow-600 px-3 py-1.5 text-sm text-white hover:bg-yellow-700 disabled:opacity-50"
            >
              Needs Revision
            </button>
            <button
              onClick={() => handleSubmit("rejected")}
              disabled={submitMutation.isPending}
              className="rounded-lg bg-red-600 px-3 py-1.5 text-sm text-white hover:bg-red-700 disabled:opacity-50"
            >
              Reject
            </button>
          </div>
          {submitMutation.isSuccess && (
            <p className="text-sm text-green-600">Submitted successfully</p>
          )}
          {submitMutation.isError && (
            <p className="text-sm text-red-600">Submission failed, please retry</p>
          )}
        </div>
      )}
    </div>
  );
}

interface ReviewableTask {
  task_id: string;
  title: string;
  status: string;
  ewu: number;
  verification_status: string;
  signal_count: number;
}

function ReviewableTaskRow({ task }: { task: ReviewableTask }) {
  const statusColor = TASK_STATUS_COLORS[task.status] ?? "text-gray-400";
  const verificationColor =
    VERIFICATION_COLORS[task.verification_status ?? "unverified"] ??
    "text-gray-500";

  return (
    <div className="rounded-lg border border-gray-800 bg-gray-900 p-4 flex items-center justify-between gap-4">
      <div className="flex flex-col gap-1.5 min-w-0">
        <span className="font-mono text-sm text-gray-200 truncate">
          {task.title}
        </span>
        <div className="flex items-center gap-3 text-xs font-mono">
          <span className={statusColor}>{task.status}</span>
          <span className="text-gray-600">|</span>
          <span className="text-cyan-400">ewu: {task.ewu}</span>
          <span className="text-gray-600">|</span>
          <span className="text-green-400/70">
            {task.signal_count} signal{task.signal_count !== 1 ? "s" : ""}
          </span>
        </div>
      </div>
      <span
        className={`text-xs font-mono px-2 py-0.5 rounded ${verificationColor} bg-gray-800`}
      >
        {task.verification_status ?? "unverified"}
      </span>
    </div>
  );
}
