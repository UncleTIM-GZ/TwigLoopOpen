"use client";

import Link from "next/link";
import { useMe } from "@/hooks/use-auth";

export default function PublicBenefitRequestsPage() {
  const { data: meRes, isLoading } = useMe();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="text-gray-500 font-mono text-sm">loading...</p>
      </div>
    );
  }

  const actor = meRes?.data?.actor;
  if (!actor) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-4">
        <p className="text-gray-400">Please log in to view your requests.</p>
        <Link
          href="/login"
          className="text-green-400 hover:underline text-sm"
        >
          Log In
        </Link>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="font-mono text-2xl font-bold text-green-400 mb-1">
          My Requests
        </h1>
        <p className="text-sm text-gray-500">
          Organization:{" "}
          <span className="text-gray-300">{actor.display_name}</span>
        </p>
      </div>

      {/* Empty state */}
      <div className="rounded-md border border-gray-800 p-8 text-center">
        <p className="text-gray-400 text-sm mb-4">
          During Public Beta, request tracking is managed via email. Check your
          inbox for status updates.
        </p>
        <Link
          href="/public-benefit/apply"
          className="text-green-400 hover:underline text-sm"
        >
          Submit a new request
        </Link>
      </div>

      <div className="mt-8">
        <Link
          href="/public-benefit/apply"
          className="inline-block rounded-md border border-gray-700 px-4 py-2 text-sm text-gray-300 hover:border-green-400 hover:text-green-400 transition-colors"
        >
          + New Request
        </Link>
      </div>
    </div>
  );
}
