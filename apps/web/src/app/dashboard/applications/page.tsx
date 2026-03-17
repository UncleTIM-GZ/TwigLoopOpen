"use client";

import Link from "next/link";
import { useMe } from "@/hooks/use-auth";
import { useMyApplications } from "@/hooks/use-dashboard";

const STATUS_COLORS: Record<string, string> = {
  pending: "text-yellow-400",
  accepted: "text-green-400",
  rejected: "text-red-400",
  withdrawn: "text-gray-500",
};

export default function ApplicationsPage() {
  const { data: meRes, isLoading: meLoading } = useMe();
  const { data: appsRes, isLoading: appsLoading } = useMyApplications();

  if (meLoading || appsLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <p className="text-gray-500 font-mono text-sm">loading...</p>
      </div>
    );
  }

  const actor = meRes?.data?.actor;
  if (!actor) {
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

  const applications = appsRes?.data ?? [];

  return (
    <div className="bg-gray-950 rounded-xl p-6 md:p-8 space-y-8 text-gray-100">
      {/* Header */}
      <div className="border-b border-gray-800 pb-6">
        <h1 className="text-2xl font-bold font-mono text-green-400 mb-1">
          ~/dashboard/applications
        </h1>
        <p className="text-sm text-gray-500 font-mono">
          applications submitted by {actor.display_name}
        </p>
      </div>

      {/* Applications List */}
      {applications.length === 0 ? (
        <EmptyState />
      ) : (
        <div className="flex flex-col gap-3">
          {applications.map((app) => (
            <ApplicationRow key={app.application_id} application={app} />
          ))}
        </div>
      )}

      {/* Back link */}
      <div>
        <Link
          href="/dashboard"
          className="text-sm font-mono text-gray-500 hover:text-green-400 transition-colors"
        >
          {"<"} back to dashboard
        </Link>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="rounded-lg border border-gray-800 bg-gray-900 p-8 text-center">
      <p className="text-gray-500 font-mono text-sm mb-2">
        No applications submitted yet.
      </p>
      <p className="text-gray-600 font-mono text-xs">
        Browse projects and apply to start collaborating.
      </p>
    </div>
  );
}

interface ApplicationItem {
  application_id: string;
  project_id: string;
  seat_preference: string;
  intended_role: string;
  status: string;
  created_at: string;
}

function ApplicationRow({ application }: { application: ApplicationItem }) {
  const statusColor = STATUS_COLORS[application.status] ?? "text-gray-400";
  const appliedDate = new Date(application.created_at).toLocaleDateString(
    "en-US",
    { year: "numeric", month: "short", day: "numeric" },
  );

  return (
    <Link
      href={`/projects/${application.project_id}`}
      className="rounded-lg border border-gray-800 bg-gray-900 p-4 flex items-center justify-between gap-4 hover:border-green-400/30 transition-colors"
    >
      <div className="flex flex-col gap-1.5 min-w-0">
        <span className="font-mono text-sm text-gray-200 truncate">
          project: {application.project_id.slice(0, 8)}...
        </span>
        <div className="flex items-center gap-3 text-xs font-mono">
          <span className="text-cyan-400">{application.intended_role}</span>
          <span className="text-gray-600">|</span>
          <span className="text-gray-500">
            seat: {application.seat_preference}
          </span>
          <span className="text-gray-600">|</span>
          <span className="text-gray-500">{appliedDate}</span>
        </div>
      </div>
      <span
        className={`text-xs font-mono px-2 py-0.5 rounded ${statusColor} bg-gray-800 shrink-0`}
      >
        {application.status}
      </span>
    </Link>
  );
}
