"use client";

import { useState } from "react";
import Link from "next/link";
import { useMe } from "@/hooks/use-auth";
import { usePendingReviews, useSubmitReview } from "@/hooks/use-reviews";

export default function ReviewerDashboardPage() {
  const { data: meRes, isLoading: meLoading } = useMe();
  const { data: reviewsRes, isLoading: reviewsLoading } = usePendingReviews();

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

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Reviewer Panel</h1>
        <Link href="/dashboard" className="text-sm underline">
          Back to Dashboard
        </Link>
      </div>

      <section>
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
