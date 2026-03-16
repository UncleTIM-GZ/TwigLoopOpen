"use client";

import { useState } from "react";
import Link from "next/link";
import { useMe } from "@/hooks/use-auth";
import { useMySupports, useCreateSupport } from "@/hooks/use-sponsors";

export default function SponsorDashboardPage() {
  const { data: meRes, isLoading: meLoading } = useMe();
  const { data: supportsRes, isLoading: supportsLoading } = useMySupports();

  if (meLoading) return <p className="text-muted-foreground">Loading...</p>;

  const actor = meRes?.data?.actor;
  if (!actor?.is_sponsor) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground mb-4">
          Only Sponsor role can access this page
        </p>
        <Link href="/dashboard" className="underline">
          Back to Dashboard
        </Link>
      </div>
    );
  }

  const supports = supportsRes?.data ?? [];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Sponsor Panel</h1>
        <Link href="/dashboard" className="text-sm underline">
          Back to Dashboard
        </Link>
      </div>

      <CreateSupportForm />

      <section className="mt-8">
        <h2 className="text-lg font-semibold mb-3">
          My Support Records ({supports.length})
        </h2>
        {supportsLoading ? (
          <p className="text-muted-foreground">Loading...</p>
        ) : supports.length === 0 ? (
          <p className="text-muted-foreground">No support records yet</p>
        ) : (
          <div className="grid gap-2">
            {supports.map((s) => (
              <div key={s.support_id} className="border rounded-lg p-3">
                <div className="flex justify-between">
                  <Link
                    href={`/projects/${s.project_id}`}
                    className="font-medium hover:underline"
                  >
                    Project {s.project_id.slice(0, 8)}...
                  </Link>
                  <span className="text-xs text-muted-foreground">
                    {s.status}
                  </span>
                </div>
                <div className="text-sm text-muted-foreground mt-1">
                  <span>Type: {supportTypeLabel(s.support_type)}</span>
                  {s.amount != null && <span> | Amount: {s.amount}</span>}
                  <span>
                    {" "}
                    | {new Date(s.created_at).toLocaleDateString("en-US")}
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
      <h2 className="text-lg font-semibold mb-3">New Support</h2>
      <form onSubmit={handleSubmit} className="border rounded-lg p-4 space-y-3">
        <div>
          <label className="text-sm font-medium">Project ID</label>
          <input
            type="text"
            className="w-full border rounded-lg p-2 text-sm mt-1"
            placeholder="Enter project UUID"
            value={projectId}
            onChange={(e) => setProjectId(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="text-sm font-medium">Support Type</label>
          <select
            className="w-full border rounded-lg p-2 text-sm mt-1"
            value={supportType}
            onChange={(e) =>
              setSupportType(
                e.target.value as "financial" | "resource" | "mentorship",
              )
            }
          >
            <option value="financial">Financial</option>
            <option value="resource">Resource</option>
            <option value="mentorship">Mentorship</option>
          </select>
        </div>
        {supportType === "financial" && (
          <div>
            <label className="text-sm font-medium">Amount</label>
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
          {createMutation.isPending ? "Submitting..." : "Submit Support"}
        </button>
        {createMutation.isSuccess && (
          <p className="text-sm text-green-600">Submitted successfully</p>
        )}
        {createMutation.isError && (
          <p className="text-sm text-red-600">Submission failed, please retry</p>
        )}
      </form>
    </section>
  );
}

function supportTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    financial: "Financial",
    resource: "Resource",
    mentorship: "Mentorship",
  };
  return labels[type] ?? type;
}
