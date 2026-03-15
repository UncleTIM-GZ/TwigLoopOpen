"use client";

import { useState } from "react";
import Link from "next/link";
import { useMe } from "@/hooks/use-auth";
import { useMySupports, useCreateSupport } from "@/hooks/use-sponsors";

export default function SponsorDashboardPage() {
  const { data: meRes, isLoading: meLoading } = useMe();
  const { data: supportsRes, isLoading: supportsLoading } = useMySupports();

  if (meLoading) return <p className="text-muted-foreground">加载中...</p>;

  const actor = meRes?.data?.actor;
  if (!actor?.is_sponsor) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground mb-4">
          仅 Sponsor 角色可访问此页面
        </p>
        <Link href="/dashboard" className="underline">
          返回工作台
        </Link>
      </div>
    );
  }

  const supports = supportsRes?.data ?? [];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Sponsor 工作台</h1>
        <Link href="/dashboard" className="text-sm underline">
          返回工作台
        </Link>
      </div>

      <CreateSupportForm />

      <section className="mt-8">
        <h2 className="text-lg font-semibold mb-3">
          我的支持记录 ({supports.length})
        </h2>
        {supportsLoading ? (
          <p className="text-muted-foreground">加载中...</p>
        ) : supports.length === 0 ? (
          <p className="text-muted-foreground">暂无支持记录</p>
        ) : (
          <div className="grid gap-2">
            {supports.map((s) => (
              <div key={s.support_id} className="border rounded-lg p-3">
                <div className="flex justify-between">
                  <Link
                    href={`/projects/${s.project_id}`}
                    className="font-medium hover:underline"
                  >
                    项目 {s.project_id.slice(0, 8)}...
                  </Link>
                  <span className="text-xs text-muted-foreground">
                    {s.status}
                  </span>
                </div>
                <div className="text-sm text-muted-foreground mt-1">
                  <span>类型: {supportTypeLabel(s.support_type)}</span>
                  {s.amount != null && <span> | 金额: {s.amount}</span>}
                  <span>
                    {" "}
                    | {new Date(s.created_at).toLocaleDateString("zh-CN")}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function CreateSupportForm() {
  const [projectId, setProjectId] = useState("");
  const [supportType, setSupportType] = useState<
    "financial" | "resource" | "mentorship"
  >("resource");
  const [amount, setAmount] = useState("");
  const createMutation = useCreateSupport();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId.trim()) return;
    createMutation.mutate({
      project_id: projectId.trim(),
      support_type: supportType,
      amount: amount ? Number(amount) : undefined,
    });
  };

  return (
    <section>
      <h2 className="text-lg font-semibold mb-3">新增支持</h2>
      <form onSubmit={handleSubmit} className="border rounded-lg p-4 space-y-3">
        <div>
          <label className="text-sm font-medium">项目 ID</label>
          <input
            type="text"
            className="w-full border rounded-lg p-2 text-sm mt-1"
            placeholder="输入项目 UUID"
            value={projectId}
            onChange={(e) => setProjectId(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="text-sm font-medium">支持类型</label>
          <select
            className="w-full border rounded-lg p-2 text-sm mt-1"
            value={supportType}
            onChange={(e) =>
              setSupportType(
                e.target.value as "financial" | "resource" | "mentorship",
              )
            }
          >
            <option value="financial">资金</option>
            <option value="resource">资源</option>
            <option value="mentorship">导师指导</option>
          </select>
        </div>
        {supportType === "financial" && (
          <div>
            <label className="text-sm font-medium">金额</label>
            <input
              type="number"
              className="w-full border rounded-lg p-2 text-sm mt-1"
              placeholder="0.00"
              min="0"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
          </div>
        )}
        <button
          type="submit"
          disabled={createMutation.isPending || !projectId.trim()}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/80 disabled:opacity-50"
        >
          {createMutation.isPending ? "提交中..." : "提交支持"}
        </button>
        {createMutation.isSuccess && (
          <p className="text-sm text-green-600">提交成功</p>
        )}
        {createMutation.isError && (
          <p className="text-sm text-red-600">提交失败，请重试</p>
        )}
      </form>
    </section>
  );
}

function supportTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    financial: "资金",
    resource: "资源",
    mentorship: "导师指导",
  };
  return labels[type] ?? type;
}
