"use client";

import { use } from "react";
import Link from "next/link";
import {
  useProject,
  useWorkPackages,
  useSeats,
  useProjectTasks,
} from "@/hooks/use-projects";
import type { TaskCardResponse } from "@/types/api";

const TYPE_LABELS: Record<string, string> = {
  general: "general",
  public_benefit: "public_benefit",
  recruitment: "recruitment",
};

const TYPE_COLORS: Record<string, string> = {
  general: "bg-cyan-400/10 text-cyan-400 border-cyan-400/20",
  public_benefit: "bg-yellow-400/10 text-yellow-400 border-yellow-400/20",
  recruitment: "bg-purple-400/10 text-purple-400 border-purple-400/20",
};

export default function ProjectDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data: projRes, isLoading: projLoading } = useProject(id);
  const { data: wpRes } = useWorkPackages(id);
  const { data: seatRes } = useSeats(id);
  const { data: taskRes } = useProjectTasks(id);

  if (projLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <p className="text-gray-500 font-mono text-sm">loading...</p>
      </div>
    );
  }

  const project = projRes?.data;
  if (!project) {
    return (
      <div className="min-h-[40vh] flex items-center justify-center bg-gray-950 rounded-xl p-8">
        <p className="text-red-400 font-mono text-sm">
          error: project not found
        </p>
      </div>
    );
  }

  const workPackages = wpRes?.data ?? [];
  const allTasks = taskRes?.data ?? [];
  const tasksByWp: Record<string, TaskCardResponse[]> = {};
  for (const task of allTasks) {
    const wpId = task.work_package_id;
    if (!tasksByWp[wpId]) tasksByWp[wpId] = [];
    tasksByWp[wpId].push(task);
  }
  const seats = seatRes?.data ?? [];
  const neededRoles = seats
    .filter((s) => s.status === "open" || !s.actor_id)
    .map((s) => s.role_needed);
  const uniqueRoles = [...new Set(neededRoles)];

  // Top 1-3 work packages as "current task directions"
  const topDirections = workPackages
    .filter((wp) => wp.status !== "done" && wp.status !== "cancelled")
    .slice(0, 3);

  return (
    <div className="bg-gray-950 rounded-xl p-6 md:p-8 text-gray-100 max-w-3xl">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 mb-6 text-sm font-mono">
        <Link
          href="/projects"
          className="text-gray-500 hover:text-green-400 transition-colors"
        >
          ~/projects
        </Link>
        <span className="text-gray-700">/</span>
        <span className="text-green-400 truncate max-w-[200px]">
          {project.title}
        </span>
      </div>

      {/* Project Header */}
      <section className="border-b border-gray-800 pb-6 mb-8">
        <div className="flex flex-wrap items-start gap-3 mb-3">
          <h1 className="text-2xl font-bold font-mono text-green-400">
            {project.title}
          </h1>
          <span
            className={`text-xs font-mono px-2 py-0.5 rounded border ${
              TYPE_COLORS[project.project_type] ?? "bg-gray-800 text-gray-400 border-gray-700"
            }`}
          >
            {TYPE_LABELS[project.project_type] ?? project.project_type}
          </span>
        </div>
        <div className="flex flex-wrap gap-4 text-sm font-mono">
          <InfoPill label="status" value={project.status} />
          <InfoPill label="stage" value={project.current_stage} />
          {project.has_reward && (
            <span className="text-green-400 text-xs bg-green-400/10 px-2 py-0.5 rounded">
              has_reward
            </span>
          )}
          {project.has_sponsor && (
            <span className="text-cyan-400 text-xs bg-cyan-400/10 px-2 py-0.5 rounded">
              has_sponsor
            </span>
          )}
        </div>
      </section>

      {/* Summary */}
      <section className="mb-8">
        <SectionHeading>summary</SectionHeading>
        <p className="text-sm text-gray-300 font-mono leading-relaxed">
          {project.summary}
        </p>
      </section>

      {/* Target Users */}
      {project.target_users && (
        <section className="mb-8">
          <SectionHeading>target_users</SectionHeading>
          <p className="text-sm text-gray-300 font-mono">{project.target_users}</p>
        </section>
      )}

      {/* Min Start Step */}
      {project.min_start_step && (
        <section className="mb-8">
          <SectionHeading>min_start_step</SectionHeading>
          <p className="text-sm text-gray-300 font-mono">{project.min_start_step}</p>
        </section>
      )}

      {/* Needed Roles */}
      {uniqueRoles.length > 0 && (
        <section className="mb-8">
          <SectionHeading>needed roles</SectionHeading>
          <div className="flex flex-wrap gap-2">
            {uniqueRoles.map((role) => (
              <span
                key={role}
                className="text-xs font-mono bg-cyan-400/10 text-cyan-400 border border-cyan-400/20 px-3 py-1 rounded"
              >
                {role}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* Current Task Directions (top 1-3 work packages) */}
      {topDirections.length > 0 && (
        <section className="mb-8">
          <SectionHeading>current task directions</SectionHeading>
          <div className="grid gap-2">
            {topDirections.map((wp, i) => {
              const wpTasks = tasksByWp[wp.work_package_id] ?? [];
              return (
                <div
                  key={wp.work_package_id}
                  className="bg-gray-900 border border-gray-800 rounded-lg p-4"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3">
                      <span className="text-xs font-mono text-gray-600 mt-0.5">
                        {String(i + 1).padStart(2, "0")}
                      </span>
                      <div>
                        <span className="font-mono text-sm text-gray-200">
                          {wp.title}
                        </span>
                        {wp.description && (
                          <p className="text-xs text-gray-500 font-mono mt-1">
                            {wp.description}
                          </p>
                        )}
                      </div>
                    </div>
                    <span className="text-xs font-mono text-gray-600 shrink-0">
                      {wp.status}
                    </span>
                  </div>
                  {wpTasks.length > 0 && (
                    <div className="mt-3 ml-8 flex flex-col gap-1.5">
                      {wpTasks.map((task) => (
                        <TaskBrief key={task.task_id} task={task} />
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* All Work Packages (if more than top directions) */}
      {workPackages.length > topDirections.length && (
        <section className="mb-8">
          <SectionHeading>all work packages</SectionHeading>
          <div className="grid gap-2">
            {workPackages.map((wp) => {
              const wpTasks = tasksByWp[wp.work_package_id] ?? [];
              return (
                <div
                  key={wp.work_package_id}
                  className="bg-gray-900 border border-gray-800 rounded-lg p-3"
                >
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-sm text-gray-300">
                      {wp.title}
                    </span>
                    <span className="text-xs font-mono text-gray-600">
                      {wp.status}
                    </span>
                  </div>
                  {wpTasks.length > 0 && (
                    <div className="mt-2 flex flex-col gap-1.5">
                      {wpTasks.map((task) => (
                        <TaskBrief key={task.task_id} task={task} />
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Seats */}
      {seats.length > 0 && (
        <section className="mb-8">
          <SectionHeading>collaboration seats</SectionHeading>
          <div className="grid gap-2">
            {seats.map((s) => (
              <div
                key={s.seat_id}
                className="bg-gray-900 border border-gray-800 rounded-lg p-3 flex justify-between items-center"
              >
                <span className="font-mono text-sm text-gray-300">
                  <span className="text-cyan-400">{s.role_needed}</span>
                  <span className="text-gray-600 mx-2">/</span>
                  <span className="text-gray-500">{s.seat_type}</span>
                </span>
                <span
                  className={`text-xs font-mono ${
                    s.status === "open" ? "text-green-400" : "text-gray-600"
                  }`}
                >
                  {s.status}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Public Benefit Rules Notice */}
      {project.project_type === "public_benefit" && (
        <section className="mb-8">
          <div className="bg-yellow-400/5 border border-yellow-400/20 rounded-lg p-4">
            <h3 className="text-xs font-mono text-yellow-400 uppercase tracking-wider mb-2">
              public benefit notice
            </h3>
            <p className="text-sm text-yellow-300/70 font-mono leading-relaxed">
              This is a public benefit project. It requires mandatory human
              review at key milestones. Progress and outcomes are subject to
              community transparency standards.
            </p>
            {project.needs_human_reviewer && (
              <p className="text-xs text-yellow-400/60 font-mono mt-2">
                review_status: {project.human_review_status}
              </p>
            )}
          </div>
        </section>
      )}

      {/* Human Review Notice (non-public_benefit but needs reviewer) */}
      {project.project_type !== "public_benefit" &&
        project.needs_human_reviewer && (
          <section className="mb-8">
            <div className="bg-orange-400/5 border border-orange-400/20 rounded-lg p-4">
              <p className="text-sm text-orange-300/70 font-mono">
                human review required -- status: {project.human_review_status}
              </p>
            </div>
          </section>
        )}

      {/* Application Method */}
      <section className="mb-4">
        <SectionHeading>apply</SectionHeading>
        <p className="text-sm text-gray-400 font-mono mb-4">
          Interested in this project? Submit an application to join the
          collaboration.
        </p>
        <Link
          href={`/projects/${id}/apply`}
          className="inline-flex items-center gap-2 rounded-lg bg-green-400/10 border border-green-400/30 px-5 py-2.5 text-sm font-mono text-green-400 hover:bg-green-400/20 hover:border-green-400/50 transition-colors"
        >
          <span>{">"}</span>
          apply to join
        </Link>
      </section>
    </div>
  );
}

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-xs font-mono text-cyan-400 uppercase tracking-wider mb-3">
      {children}
    </h2>
  );
}

function InfoPill({ label, value }: { label: string; value: string }) {
  return (
    <span className="text-xs font-mono text-gray-400">
      <span className="text-gray-600">{label}:</span>{" "}
      <span className="text-gray-300">{value}</span>
    </span>
  );
}

const TASK_VERIFICATION_COLORS: Record<string, string> = {
  unverified: "text-gray-500 bg-gray-800",
  pending: "text-yellow-400 bg-yellow-400/10",
  verified: "text-green-400 bg-green-400/10",
  rejected: "text-red-400 bg-red-400/10",
};

function TaskBrief({ task }: { task: TaskCardResponse }) {
  const verificationStyle =
    TASK_VERIFICATION_COLORS[task.verification_status] ??
    "text-gray-500 bg-gray-800";

  const signalQuality =
    task.signal_count >= 3
      ? "strong"
      : task.signal_count >= 1
        ? "partial"
        : "none";
  const signalColor =
    signalQuality === "strong"
      ? "text-green-400"
      : signalQuality === "partial"
        ? "text-yellow-400"
        : "text-gray-500";

  return (
    <div className="bg-gray-800/50 rounded px-3 py-2 text-xs font-mono space-y-1">
      {/* Row 1: title + status */}
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-gray-300 truncate">{task.title}</span>
          <span className="text-gray-600">|</span>
          <span className="text-gray-500">{task.status}</span>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-cyan-400">ewu:{task.ewu}</span>
          <span className={`px-1.5 py-0.5 rounded ${verificationStyle}`}>
            {task.verification_status}
          </span>
          {task.completion_mode === "legacy" && (
            <span className="text-orange-400/70 bg-orange-400/10 px-1.5 py-0.5 rounded">
              legacy
            </span>
          )}
        </div>
      </div>

      {/* Row 2: signal info (if any signals exist) */}
      {task.signal_count > 0 && (
        <div className="flex items-center gap-3 text-gray-500 pl-1">
          <span className={signalColor}>
            signal: {signalQuality} ({task.signal_count})
          </span>
          {task.pr_url && (
            <a
              href={task.pr_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-cyan-400/70 hover:text-cyan-400 truncate max-w-[200px]"
            >
              PR
            </a>
          )}
          {task.latest_commit_sha && (
            <span className="text-gray-600">
              commit: {task.latest_commit_sha.slice(0, 7)}
            </span>
          )}
          <span className="text-gray-700 italic">
            signal is advisory, not proof of completion
          </span>
        </div>
      )}
    </div>
  );
}
