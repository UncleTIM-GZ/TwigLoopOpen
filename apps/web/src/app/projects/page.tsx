"use client";

import { useState } from "react";
import Link from "next/link";
import { useProjects } from "@/hooks/use-projects";

const TYPE_LABELS: Record<string, string> = {
  general: "General",
  public_benefit: "Public Benefit",
  recruitment: "Recruitment",
};

const TYPE_COLORS: Record<string, string> = {
  general: "text-cyan-400 border-cyan-400/40 bg-cyan-400/10",
  public_benefit: "text-green-400 border-green-400/40 bg-green-400/10",
  recruitment: "text-yellow-400 border-yellow-400/40 bg-yellow-400/10",
};

const STATUS_COLORS: Record<string, string> = {
  draft: "text-gray-500",
  published: "text-green-400",
  in_progress: "text-cyan-400",
  completed: "text-gray-400",
  archived: "text-gray-600",
};

interface FilterTab {
  key: string;
  label: string;
  filter?: Record<string, string>;
}

const FILTER_TABS: FilterTab[] = [
  { key: "all", label: "All" },
  { key: "public_benefit", label: "Public Benefit", filter: { project_type: "public_benefit" } },
  { key: "recruitment", label: "Recruitment", filter: { project_type: "recruitment" } },
  { key: "general", label: "General", filter: { project_type: "general" } },
  { key: "open", label: "Open for Application", filter: { status: "published" } },
];

export default function ProjectsPage() {
  const [activeTab, setActiveTab] = useState("all");
  const currentTab = FILTER_TABS.find((t) => t.key === activeTab);
  const filters = currentTab?.filter;
  const { data: res, isLoading } = useProjects(filters);

  const projects = res?.data ?? [];
  const meta = res?.meta as { total?: number } | null;

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="font-mono text-sm text-gray-500 mb-2">
          $ ls /projects --format=list
        </h1>
        <h2 className="font-mono text-2xl font-bold text-gray-100">
          Project Feed
        </h2>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {FILTER_TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`font-mono text-xs px-3 py-1.5 border transition-colors ${
              activeTab === tab.key
                ? "border-green-400/40 bg-green-400/10 text-green-400"
                : "border-gray-800 text-gray-500 hover:text-gray-300 hover:border-gray-700"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="border border-gray-800 p-8 text-center">
          <p className="font-mono text-sm text-gray-600 animate-pulse">
            Fetching projects...
          </p>
        </div>
      )}

      {/* Empty */}
      {!isLoading && projects.length === 0 && (
        <div className="border border-gray-800 p-8 text-center">
          <p className="font-mono text-sm text-gray-600">
            No projects found
          </p>
          <p className="font-mono text-xs text-gray-700 mt-1">
            Try a different filter or check back later
          </p>
        </div>
      )}

      {/* Project List */}
      <div className="grid gap-3">
        {projects.map((p) => (
          <Link
            key={p.project_id}
            href={`/projects/${p.project_id}`}
            className="border border-gray-800 p-5 hover:border-green-400/20 transition-colors group"
          >
            <div className="flex items-start justify-between mb-3">
              <h3 className="font-mono text-sm font-semibold text-gray-100 group-hover:text-green-400 transition-colors">
                {p.title}
              </h3>
              <span
                className={`font-mono text-xs px-2 py-0.5 border shrink-0 ml-3 ${
                  TYPE_COLORS[p.project_type] ?? "text-gray-400 border-gray-700"
                }`}
              >
                {TYPE_LABELS[p.project_type] ?? p.project_type}
              </span>
            </div>

            <p className="font-mono text-xs text-gray-500 line-clamp-2 mb-3 leading-relaxed">
              {p.summary}
            </p>

            <div className="flex flex-wrap gap-3 font-mono text-xs">
              <span className="text-gray-600">
                stage:{" "}
                <span className="text-gray-400">{p.current_stage}</span>
              </span>
              <span className={STATUS_COLORS[p.status] ?? "text-gray-400"}>
                status: {p.status}
              </span>
              {p.has_reward && (
                <span className="text-green-400">
                  has-reward
                </span>
              )}
              {p.needs_human_reviewer && (
                <span className="text-yellow-400">
                  review-required
                </span>
              )}
            </div>
          </Link>
        ))}
      </div>

      {/* Total Count */}
      {meta?.total != null && (
        <p className="mt-6 font-mono text-xs text-gray-600">
          Total: {meta.total} project{meta.total !== 1 ? "s" : ""}
        </p>
      )}
    </div>
  );
}
