"use client";

import { useProjects } from "@/hooks/use-projects";

const SYSTEM_NOTES = [
  "Platform is in Public Beta",
  "Core workflows operational: project creation, applications, task cards",
  "Source sync via GitHub webhooks is active",
  "ClickHouse analytics pipeline ready",
  "MCP protocol integration available",
];

export default function StatusPage() {
  const { data: projRes } = useProjects();
  const projects = projRes?.data ?? [];

  const openProjects = projects.filter(
    (p) => p.status === "open_for_collaboration" || p.status === "team_forming",
  );
  const totalTasks = projects.reduce(
    (sum, p) => sum + Number(p.task_count ?? 0),
    0,
  );
  const totalEwu = projects.reduce(
    (sum, p) => sum + parseFloat(String(p.total_ewu ?? 0)),
    0,
  );
  const avgEwu =
    totalTasks > 0
      ? (totalEwu / totalTasks).toFixed(1)
      : "—";
  const maxEwu = projects.reduce(
    (max, p) => Math.max(max, parseFloat(String(p.max_ewu ?? 0))),
    0,
  );

  const statusLevel = "Public Beta";
  const statusColor = "text-green-400";
  const statusBorder = "border-green-400/40";
  const statusBg = "bg-green-400/10";

  return (
    <div className="space-y-12">
      {/* Header */}
      <section>
        <h1 className="font-mono text-sm text-gray-500 mb-4">
          $ status --verbose
        </h1>
        <div className="flex items-center gap-4">
          <h2 className="font-mono text-2xl font-bold text-gray-100">
            Platform Status
          </h2>
          <span
            className={`font-mono text-xs px-3 py-1 border ${statusBorder} ${statusBg} ${statusColor}`}
          >
            {statusLevel}
          </span>
        </div>
      </section>

      {/* Core Metrics (live) */}
      <section>
        <h2 className="font-mono text-sm text-gray-500 mb-4">
          $ metrics --core
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <MetricCard label="Total Projects" value={projects.length} />
          <MetricCard label="Open Projects" value={openProjects.length} />
          <MetricCard label="Total Tasks" value={totalTasks} />
          <MetricCard label="Total EWU" value={totalEwu} />
          <MetricCard label="Avg EWU" value={avgEwu} />
          <MetricCard label="Max EWU" value={maxEwu} />
        </div>
      </section>

      {/* Project Breakdown */}
      {projects.length > 0 && (
        <section>
          <h2 className="font-mono text-sm text-gray-500 mb-4">
            $ ls projects/
          </h2>
          <div className="border border-gray-800 divide-y divide-gray-800">
            {projects.map((p) => (
              <div
                key={p.project_id}
                className="flex items-center justify-between p-4"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className="font-mono text-sm text-gray-200 truncate">
                    {p.title}
                  </span>
                  <span className="font-mono text-xs text-gray-600">
                    {p.project_type}
                  </span>
                </div>
                <StatusBadge status={p.status} />
              </div>
            ))}
          </div>
        </section>
      )}

      {/* System Notes */}
      <section>
        <h2 className="font-mono text-sm text-gray-500 mb-4">
          $ cat /etc/twigloop/notes
        </h2>
        <div className="border border-gray-800 p-5 space-y-2">
          {SYSTEM_NOTES.map((note, i) => (
            <p key={i} className="font-mono text-xs text-gray-400">
              <span className="text-gray-600 mr-2">#</span>
              {note}
            </p>
          ))}
        </div>
      </section>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="border border-gray-800 p-5">
      <div className="font-mono text-3xl text-green-400 font-bold">
        {value}
      </div>
      <div className="font-mono text-xs text-gray-500 mt-2">
        {label}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colorMap: Record<string, string> = {
    open: "text-green-400 border-green-400/40 bg-green-400/10",
    draft: "text-yellow-400 border-yellow-400/40 bg-yellow-400/10",
    closed: "text-gray-500 border-gray-700 bg-gray-800",
    archived: "text-gray-600 border-gray-700 bg-gray-900",
  };

  const classes = colorMap[status] ?? "text-gray-400 border-gray-700 bg-gray-800";

  return (
    <span className={`font-mono text-xs px-2 py-0.5 border rounded ${classes}`}>
      {status}
    </span>
  );
}
