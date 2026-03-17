"use client";

import Link from "next/link";
import { useMe, useMyCredentials } from "@/hooks/use-auth";
import type { CredentialResponse } from "@/hooks/use-auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-400/10 text-gray-400 border-gray-400/20",
  issued: "bg-green-400/10 text-green-400 border-green-400/20",
  revoked: "bg-red-400/10 text-red-400 border-red-400/20",
  superseded: "bg-yellow-400/10 text-yellow-400 border-yellow-400/20",
  suspended: "bg-orange-400/10 text-orange-400 border-orange-400/20",
  expired: "bg-gray-400/10 text-gray-500 border-gray-400/20",
};

export default function CredentialsPage() {
  const { data: meRes, isLoading: meLoading } = useMe();
  const { data: credRes, isLoading: credLoading } = useMyCredentials();

  if (meLoading || credLoading) {
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

  const credentials = credRes?.data ?? [];
  const issued = credentials.filter((c) => c.status === "issued");
  const other = credentials.filter((c) => c.status !== "issued");

  return (
    <div className="bg-gray-950 rounded-xl p-6 md:p-8 space-y-8 text-gray-100">
      {/* Header */}
      <div className="border-b border-gray-800 pb-6">
        <h1 className="text-2xl font-bold font-mono text-green-400 mb-1">
          ~/dashboard/credentials
        </h1>
        <p className="text-sm text-gray-500 font-mono">
          verifiable credentials for {actor.display_name}
        </p>
        <div className="flex gap-4 mt-3 text-xs font-mono text-gray-500">
          <span>total: {credentials.length}</span>
          <span className="text-green-400">
            active: {issued.length}
          </span>
          {other.length > 0 && (
            <span className="text-gray-400">
              other: {other.length}
            </span>
          )}
        </div>
      </div>

      {/* Credentials List */}
      {credentials.length === 0 ? (
        <EmptyState />
      ) : (
        <div className="flex flex-col gap-3">
          {credentials.map((cred) => (
            <CredentialCard key={cred.credential_id} credential={cred} />
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
        No credentials issued yet.
      </p>
      <p className="text-gray-600 font-mono text-xs">
        Complete tasks to earn verifiable credentials.
      </p>
    </div>
  );
}

function CredentialCard({
  credential,
}: {
  credential: CredentialResponse;
}) {
  const issuedDate = credential.issued_at
    ? new Date(credential.issued_at).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      })
    : "—";

  const verifyUrl = `${API_BASE}/api/v1/credentials/verify/${credential.credential_id}`;
  const statusUrl = `${API_BASE}/api/v1/credentials/${credential.credential_id}/status`;
  const statusColor =
    STATUS_COLORS[credential.status] || STATUS_COLORS.draft;

  return (
    <div className="rounded-lg border border-gray-800 bg-gray-900 p-4 space-y-3">
      {/* Top row: type + status */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs bg-cyan-400/10 text-cyan-400 px-2 py-0.5 rounded font-mono border border-cyan-400/20">
            {credential.credential_type}
          </span>
          <span
            className={`text-xs px-2 py-0.5 rounded font-mono border ${statusColor}`}
          >
            {credential.status}
          </span>
          {credential.credential_version > 1 && (
            <span className="text-xs text-gray-500 font-mono">
              v{credential.credential_version}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {credential.status === "issued" && (
            <a
              href={verifyUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-md border border-gray-700 px-3 py-1 text-xs font-mono text-gray-300 hover:border-green-400 hover:text-green-400 transition-colors"
            >
              verify
            </a>
          )}
          <a
            href={statusUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-md border border-gray-700 px-3 py-1 text-xs font-mono text-gray-300 hover:border-cyan-400 hover:text-cyan-400 transition-colors"
          >
            status
          </a>
        </div>
      </div>

      {/* Details row */}
      <div className="flex items-center gap-3 text-xs text-gray-500 font-mono">
        <span>issued: {issuedDate}</span>
        {credential.task_id && (
          <span>
            task: {credential.task_id.slice(0, 8)}...
          </span>
        )}
        {credential.revoked_at && (
          <span className="text-red-400">
            revoked:{" "}
            {new Date(credential.revoked_at).toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
            })}
          </span>
        )}
        {credential.superseded_by && (
          <span className="text-yellow-400">
            superseded by: {credential.superseded_by.slice(0, 8)}...
          </span>
        )}
      </div>
    </div>
  );
}
