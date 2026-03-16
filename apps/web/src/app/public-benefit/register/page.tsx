"use client";

import { useState } from "react";
import Link from "next/link";

export default function PublicBenefitRegisterPage() {
  const [orgName, setOrgName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [contactName, setContactName] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    // Placeholder -- will connect to backend registration endpoint
    setTimeout(() => {
      setSubmitting(false);
      // For now, redirect manually
      window.location.href = "/public-benefit/login";
    }, 600);
  }

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-49px)]">
      <div className="w-full max-w-sm">
        <h1 className="font-mono text-2xl font-bold text-green-400 mb-1">
          Register
        </h1>
        <p className="text-sm text-gray-500 mb-8">
          Create an account for your public benefit organization.
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <label className="flex flex-col gap-1.5">
            <span className="text-sm text-gray-400">Organization Name</span>
            <input
              type="text"
              value={orgName}
              onChange={(e) => setOrgName(e.target.value)}
              required
              placeholder="Hope Foundation"
              className={inputClass}
            />
          </label>

          <label className="flex flex-col gap-1.5">
            <span className="text-sm text-gray-400">Contact Email</span>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="contact@example.org"
              className={inputClass}
            />
          </label>

          <label className="flex flex-col gap-1.5">
            <span className="text-sm text-gray-400">Password</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              placeholder="At least 8 characters"
              className={inputClass}
            />
          </label>

          <label className="flex flex-col gap-1.5">
            <span className="text-sm text-gray-400">Contact Name</span>
            <input
              type="text"
              value={contactName}
              onChange={(e) => setContactName(e.target.value)}
              placeholder="Primary contact person"
              className={inputClass}
            />
          </label>

          {error && <p className="text-sm text-red-400">{error}</p>}

          <button
            type="submit"
            disabled={submitting}
            className="mt-2 rounded-md bg-green-400 px-4 py-2.5 text-sm font-medium text-gray-950 hover:bg-green-300 disabled:opacity-50 transition-colors"
          >
            {submitting ? "Registering..." : "Register"}
          </button>
        </form>

        <p className="mt-6 text-sm text-gray-500">
          Already have an account?{" "}
          <Link
            href="/public-benefit/login"
            className="text-green-400 hover:underline"
          >
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}

const inputClass =
  "w-full rounded-md border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-gray-200 placeholder:text-gray-600 focus:border-green-400 focus:outline-none focus:ring-1 focus:ring-green-400/40 transition-colors";
