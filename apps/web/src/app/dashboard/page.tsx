"use client";

import Link from "next/link";
import { useMe, useMyCredentials } from "@/hooks/use-auth";
import { useProjects } from "@/hooks/use-projects";

const ROLE_LABELS: Record<string, string> = {
  founder: "founder",
  collaborator: "collaborator",
  reviewer: "reviewer",
  sponsor: "sponsor",
};

export default function DashboardPage() {
  const { data: meRes, isLoading: meLoading } = useMe();
  const { data: projRes } = useProjects();
  const { data: credRes } = useMyCredentials();

  if (meLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <p className="text-gray-500 font-mono text-sm">loading...</p>
      </div>
    );
  }

  const actor = meRes?.data?.actor;
  const account = meRes?.data?.account;
  if (!actor || !account) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center gap-4 bg-gray-950 rounded-xl p-8">
        <p className="text-gray-400 font-mono">not authenticated</p>
        <Link
          href="/login"
          className="text-green-400 hover:text-green-300 font-mono underline underline-offset-4"
        >
          $ login
        </Link>
      </div>
    );
  }

  const projects = projRes?.data ?? [];
  const credentials = credRes?.data ?? [];
  const myProjects = projects.filter(
    (p) => p.founder_actor_id === actor.actor_id,
  );

  const roles = [
    actor.is_founder && ROLE_LABELS.founder,
    actor.is_collaborator && ROLE_LABELS.collaborator,
    actor.is_reviewer && ROLE_LABELS.reviewer,
    actor.is_sponsor && ROLE_LABELS.sponsor,
  ].filter(Boolean) as string[];

  return (
    <div className="bg-gray-950 rounded-xl p-6 md:p-8 space-y-8 text-gray-100">
      {/* Header */}
      <div className="border-b border-gray-800 pb-6">
        <h1 className="text-2xl font-bold font-mono text-green-400 mb-1">
          ~/dashboard
        </h1>
        <p className="text-sm text-gray-500 font-mono">
          welcome back, {actor.display_name}
        </p>
      </div>

      {/* User Summary */}
      <section className="bg-gray-900 rounded-lg border border-gray-800 p-5">
        <h2 className="text-sm font-mono text-cyan-400 uppercase tracking-wider mb-4">
          user info
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm font-mono">
          <div>
            <span className="text-gray-500 block mb-1">display_name</span>
            <span className="text-gray-100">{actor.display_name}</span>
          </div>
          <div>
            <span className="text-gray-500 block mb-1">actor_type</span>
            <span className="text-gray-100">{actor.actor_type}</span>
          </div>
          <div>
            <span className="text-gray-500 block mb-1">roles</span>
            <div className="flex flex-wrap gap-1.5">
              {roles.length > 0 ? (
                roles.map((r) => (
                  <span
                    key={r}
                    className="text-xs bg-green-400/10 text-green-400 px-2 py-0.5 rounded"
                  >
                    {r}
                  </span>
                ))
              ) : (
                <span className="text-gray-600">none</span>
              )}
            </div>
          </div>
          <div>
            <span className="text-gray-500 block mb-1">profile_status</span>
            <span
              className={
                actor.profile_status === "complete"
                  ? "text-green-400"
                  : "text-yellow-400"
              }
            >
              {actor.profile_status}
            </span>
          </div>
        </div>
      </section>

      {/* Stats Cards */}
      <section>
        <h2 className="text-sm font-mono text-cyan-400 uppercase tracking-wider mb-4">
          summary
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard label="projects" value={myProjects.length} />
          <StatCard label="applications" value="--" />
          <StatCard label="active_tasks" value="--" />
          <StatCard label="records" value={credentials.length} />
        </div>
      </section>

      {/* Recent Activity */}
      <section>
        <h2 className="text-sm font-mono text-cyan-400 uppercase tracking-wider mb-4">
          recent activity
        </h2>
        <div className="bg-gray-900 rounded-lg border border-gray-800 px-4 py-6 text-center">
          <p className="text-sm text-gray-500 font-mono">
            <span className="text-gray-600 mr-2">#</span>
            activity tracking not yet available in beta
          </p>
        </div>
      </section>

      {/* My Projects */}
      {myProjects.length > 0 && (
        <section>
          <h2 className="text-sm font-mono text-cyan-400 uppercase tracking-wider mb-4">
            my projects
          </h2>
          <div className="grid gap-2">
            {myProjects.map((p) => (
              <Link
                key={p.project_id}
                href={`/projects/${p.project_id}`}
                className="bg-gray-900 border border-gray-800 rounded-lg p-3 hover:border-green-400/30 transition-colors flex justify-between items-center"
              >
                <span className="font-mono text-sm text-gray-200">
                  {p.title}
                </span>
                <span className="text-xs font-mono text-gray-500">
                  {p.status}
                </span>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Quick Links */}
      <section>
        <h2 className="text-sm font-mono text-cyan-400 uppercase tracking-wider mb-4">
          quick links
        </h2>
        <div className="flex flex-wrap gap-3">
          <QuickLink href="/dashboard/tasks" label="my tasks" />
          <QuickLink href="/dashboard/applications" label="my applications" />
          <QuickLink href="/dashboard/profile" label="edit profile" />
          <QuickLink href="/dashboard/credentials" label="my credentials" />
          <QuickLink href="/create" label="new project" />
          <QuickLink href="/projects" label="browse projects" />
          {actor.is_reviewer && (
            <QuickLink href="/dashboard/reviewer" label="reviewer panel" />
          )}
          {actor.is_sponsor && (
            <QuickLink href="/dashboard/sponsor" label="sponsor panel" />
          )}
        </div>
      </section>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
      <p className="text-xs font-mono text-gray-500 mb-2">{label}</p>
      <p className="text-2xl font-bold font-mono text-green-400">{value}</p>
    </div>
  );
}

function QuickLink({ href, label }: { href: string; label: string }) {
  return (
    <Link
      href={href}
      className="inline-flex items-center gap-2 rounded-lg border border-gray-800 bg-gray-900 px-4 py-2 text-sm font-mono text-gray-300 hover:border-green-400/40 hover:text-green-400 transition-colors"
    >
      <span className="text-green-400">{">"}</span>
      {label}
    </Link>
  );
}
