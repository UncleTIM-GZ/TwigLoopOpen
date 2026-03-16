"use client";

import Link from "next/link";
import { useProjects } from "@/hooks/use-projects";

export default function HomePage() {
  const { data: projRes } = useProjects();
  const projects = projRes?.data ?? [];
  const latest = projects.slice(0, 3);

  const totalTasks = projects.reduce(
    (sum, p) => sum + Number(p.task_count ?? 0),
    0,
  );
  const totalEwu = projects.reduce(
    (sum, p) => sum + parseFloat(String(p.total_ewu ?? 0)),
    0,
  );

  return (
    <div className="max-w-3xl mx-auto space-y-16 py-8">
      {/* Hero */}
      <section>
        <h1 className="font-mono text-5xl md:text-6xl font-bold text-green-400 tracking-tight">
          Twig Loop
        </h1>
        <p className="mt-4 font-mono text-sm text-gray-500 leading-relaxed max-w-xl">
          Structure ideas into real collaboration.
          Verified by code, not by promises.
        </p>
        <div className="mt-8 flex gap-3">
          <Link
            href="/projects"
            className="font-mono text-sm px-5 py-2 bg-green-400 text-gray-950 hover:bg-green-300 transition-colors"
          >
            Browse Projects
          </Link>
          <Link
            href="/create"
            className="font-mono text-sm px-5 py-2 border border-gray-700 text-gray-300 hover:border-green-400/40 hover:text-green-400 transition-colors"
          >
            Create Project
          </Link>
        </div>
      </section>

      {/* Status */}
      <section>
        <p className="font-mono text-sm text-gray-500 mb-4">$ status</p>
        <p className="font-mono text-sm text-gray-400">
          <span className="text-green-400">{projects.length}</span> projects
          {" · "}
          <span className="text-green-400">{totalTasks}</span> tasks
          {" · "}
          <span className="text-green-400">{totalEwu > 0 ? totalEwu.toFixed(0) : "0"}</span> EWU
        </p>
      </section>

      {/* Latest Projects */}
      {latest.length > 0 && (
        <section>
          <p className="font-mono text-sm text-gray-500 mb-4">
            $ ls projects/ --latest 3
          </p>
          <div className="space-y-1">
            {latest.map((p) => (
              <Link
                key={p.project_id}
                href={`/projects/${p.project_id}`}
                className="font-mono text-sm flex justify-between py-2 px-3 hover:bg-gray-900 transition-colors group"
              >
                <span className="text-gray-300 group-hover:text-green-400 transition-colors truncate mr-4">
                  {p.title}
                </span>
                <span className="text-gray-600 shrink-0">
                  {p.status === "open_for_collaboration" ? "open" : p.status}
                  {"  "}
                  {p.task_count ?? 0} tasks{"  "}
                  {parseFloat(String(p.total_ewu ?? 0)).toFixed(0)} EWU
                </span>
              </Link>
            ))}
          </div>
          {projects.length > 3 && (
            <Link
              href="/projects"
              className="font-mono text-xs text-green-400/60 hover:text-green-400 mt-2 inline-block transition-colors"
            >
              {">"} view all {projects.length} projects
            </Link>
          )}
        </section>
      )}

      {/* MCP */}
      <section>
        <p className="font-mono text-sm text-gray-500 mb-4">$ mcp --help</p>
        <div className="font-mono text-sm space-y-2">
          <p className="text-gray-400">
            Connect your AI assistant to Twig Loop via MCP protocol.
          </p>
          <p className="text-gray-600 text-xs mt-3">
            MCP Server deployment in progress. Currently available via local stdio mode:
          </p>
          <div className="bg-gray-950 border border-gray-800 rounded px-4 py-3 mt-2">
            <p className="text-gray-500 text-xs">
              <span className="text-gray-600">$</span>{" "}
              <span className="text-gray-400">cd apps/mcp-server</span>
            </p>
            <p className="text-gray-500 text-xs">
              <span className="text-gray-600">$</span>{" "}
              <span className="text-green-400">uv run python -m app.main</span>
            </p>
          </div>
          <p className="text-gray-600 text-xs mt-2">
            Tools: publish_project, browse_projects, apply_to_task, calculate_ewu, preflight_check
          </p>
        </div>
      </section>
    </div>
  );
}
