"use client";

import { useState } from "react";
import Link from "next/link";
import { useMe } from "@/hooks/use-auth";
import { usePendingReviews, useSubmitReview } from "@/hooks/use-reviews";

export default function ReviewerDashboardPage() {
  const { data: meRes, isLoading: meLoading } = useMe();
  const { data: reviewsRes, isLoading: reviewsLoading } = usePendingReviews();

  if (meLoading) return <p className="text-muted-foreground">加载中...</p>;

  const actor = meRes?.data?.actor;
  if (!actor?.is_reviewer) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground mb-4">
          仅复核人角色可访问此页面
        </p>
        <Link href="/dashboard" className="underline">
          返回工作台
        </Link>
      </div>
    );
  }

  const pendingItems = reviewsRes?.data ?? [];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">复核人工作台</h1>
        <Link href="/dashboard" className="text-sm underline">
          返回工作台
        </Link>
      </div>

      <section>
        <h2 className="text-lg font-semibold mb-3">
          待复核项目 ({pendingItems.length})
        </h2>
        {reviewsLoading ? (
          <p className="text-muted-foreground">加载中...</p>
        ) : pendingItems.length === 0 ? (
          <p className="text-muted-foreground">暂无待复核项目</p>
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
            项目 {item.project_id.slice(0, 8)}...
          </Link>
          <p className="text-xs text-muted-foreground">
            创建于 {new Date(item.created_at).toLocaleDateString("zh-CN")}
          </p>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-sm underline"
        >
          {expanded ? "收起" : "审核"}
        </button>
      </div>

      {expanded && (
        <div className="mt-3 space-y-3">
          <textarea
            className="w-full border rounded-lg p-2 text-sm"
            placeholder="复核意见（可选）"
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
              通过
            </button>
            <button
              onClick={() => handleSubmit("needs_revision")}
              disabled={submitMutation.isPending}
              className="rounded-lg bg-yellow-600 px-3 py-1.5 text-sm text-white hover:bg-yellow-700 disabled:opacity-50"
            >
              需修改
            </button>
            <button
              onClick={() => handleSubmit("rejected")}
              disabled={submitMutation.isPending}
              className="rounded-lg bg-red-600 px-3 py-1.5 text-sm text-white hover:bg-red-700 disabled:opacity-50"
            >
              拒绝
            </button>
          </div>
          {submitMutation.isSuccess && (
            <p className="text-sm text-green-600">提交成功</p>
          )}
          {submitMutation.isError && (
            <p className="text-sm text-red-600">提交失败，请重试</p>
          )}
        </div>
      )}
    </div>
  );
}
