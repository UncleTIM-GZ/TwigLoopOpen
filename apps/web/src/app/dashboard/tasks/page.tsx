"use client";

import Link from "next/link";
import { useMe } from "@/hooks/use-auth";
import { useMyTasks } from "@/hooks/use-dashboard";

const STATUS_COLORS: Record<string, string> = {
  draft: "text-gray-400",
  open: "text-blue-400",
  in_progress: "text-yellow-400",
  completed: "text-green-400",
  cancelled: "text-red-400",
};

const VERIFICATION_COLORS: Record<string, string> = {
  unverified: "text-gray-500",
  pending: "text-yellow-400",
  verified: "text-green-400",
  rejected: "text-red-400",
};

export default function TasksPage() {
  const { data: meRes, isLoading: meLoading } = useMe();
  const { data: tasksRes, isLoading: tasksLoading } = useMyTasks();

  if (meLoading || tasksLoading) {
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

  const tasks = tasksRes?.data ?? [];

  return (
    <div className="bg-gray-950 rounded-xl p-6 md:p-8 space-y-8 text-gray-100">
      {/* Header */}
      <div className="border-b border-gray-800 pb-6">
        <h1 className="text-2xl font-bold font-mono text-green-400 mb-1">
          ~/dashboard/tasks
        </h1>
        <p className="text-sm text-gray-500 font-mono">
          tasks assigned to {actor.display_name}
        </p>
      </div>

      {/* Task List */}
      {tasks.length === 0 ? (
        <EmptyState />
      ) : (
        <div className="flex flex-col gap-3">
          {tasks.map((task) => (
            <TaskRow key={task.task_id} task={task} />
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
        No tasks assigned yet.
      </p>
      <p className="text-gray-600 font-mono text-xs">
        Apply to a project to start receiving tasks.
      </p>
    </div>
  );
}

interface TaskItem {
  task_id: string;
  title: string;
  status: string;
  ewu: number;
  verification_status?: string;
  signal_count?: number;
  task_type?: string;
}

function TaskRow({ task }: { task: TaskItem }) {
  const statusColor = STATUS_COLORS[task.status] ?? "text-gray-400";
  const verificationColor =
    VERIFICATION_COLORS[task.verification_status ?? "unverified"] ??
    "text-gray-500";

  return (
    <div className="rounded-lg border border-gray-800 bg-gray-900 p-4 flex items-center justify-between gap-4">
      <div className="flex flex-col gap-1.5 min-w-0">
        <span className="font-mono text-sm text-gray-200 truncate">
          {task.title}
        </span>
        <div className="flex items-center gap-3 text-xs font-mono">
          <span className={statusColor}>{task.status}</span>
          <span className="text-gray-600">|</span>
          <span className="text-cyan-400">ewu: {task.ewu}</span>
          {task.task_type && (
            <>
              <span className="text-gray-600">|</span>
              <span className="text-gray-500">{task.task_type}</span>
            </>
          )}
        </div>
      </div>
      <div className="flex items-center gap-3 shrink-0">
        {(task.signal_count ?? 0) > 0 && (
          <span className="text-xs font-mono text-green-400/70">
            {task.signal_count} signal{task.signal_count !== 1 ? "s" : ""}
          </span>
        )}
        <span
          className={`text-xs font-mono px-2 py-0.5 rounded ${verificationColor} bg-gray-800`}
        >
          {task.verification_status ?? "unverified"}
        </span>
      </div>
    </div>
  );
}
