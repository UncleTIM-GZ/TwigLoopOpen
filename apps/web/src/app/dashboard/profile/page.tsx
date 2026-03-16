"use client";

import { useState } from "react";
import Link from "next/link";
import { useMe, useUpdateProfile } from "@/hooks/use-auth";

const PROJECT_TYPES = [
  { value: "general", label: "General" },
  { value: "public_benefit", label: "Public Benefit" },
  { value: "recruitment", label: "Recruitment" },
] as const;

const PREFERRED_ROLES = [
  { value: "developer", label: "Developer" },
  { value: "designer", label: "Designer" },
  { value: "reviewer", label: "Reviewer" },
  { value: "researcher", label: "Researcher" },
] as const;

export default function ProfilePage() {
  const { data: meRes, isLoading: meLoading } = useMe();
  const updateProfile = useUpdateProfile();

  const actor = meRes?.data?.actor;
  const account = meRes?.data?.account;

  const [displayName, setDisplayName] = useState("");
  const [bio, setBio] = useState("");
  const [skills, setSkills] = useState("");
  const [availability, setAvailability] = useState("");
  const [interestedTypes, setInterestedTypes] = useState<string[]>([]);
  const [preferredRoles, setPreferredRoles] = useState<string[]>([]);
  const [externalLinks, setExternalLinks] = useState("");
  const [initialized, setInitialized] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  // Populate form once when data loads
  if (actor && !initialized) {
    setDisplayName(actor.display_name ?? "");
    setBio(actor.bio ?? "");
    setAvailability(actor.availability ?? "");
    setInitialized(true);
  }

  if (meLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <p className="text-gray-500 font-mono text-sm">loading...</p>
      </div>
    );
  }

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

  function toggleCheckbox(
    value: string,
    current: string[],
    setter: (v: string[]) => void,
  ) {
    setter(
      current.includes(value)
        ? current.filter((v) => v !== value)
        : [...current, value],
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    try {
      const skillsList = skills
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);

      await updateProfile.mutateAsync({
        display_name: displayName || undefined,
        bio: bio || undefined,
        availability: availability || undefined,
        skills: skillsList.length > 0 ? skillsList : undefined,
        interested_project_types:
          interestedTypes.length > 0 ? interestedTypes : undefined,
      });
      setMessage({ type: "success", text: "profile saved successfully" });
    } catch {
      setMessage({ type: "error", text: "failed to save profile" });
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="bg-gray-950 rounded-xl p-6 md:p-8 text-gray-100 max-w-2xl">
      {/* Header */}
      <div className="border-b border-gray-800 pb-6 mb-8">
        <div className="flex items-center gap-3 mb-1">
          <Link
            href="/dashboard"
            className="text-gray-500 hover:text-green-400 font-mono text-sm transition-colors"
          >
            ~/dashboard
          </Link>
          <span className="text-gray-700 font-mono">/</span>
          <span className="text-green-400 font-mono text-sm">profile</span>
        </div>
        <h1 className="text-2xl font-bold font-mono text-green-400 mt-2">
          edit profile
        </h1>
        <p className="text-sm text-gray-500 font-mono mt-1">
          {account.email}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Display Name */}
        <FieldGroup label="display_name">
          <input
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="Your display name"
            className="w-full bg-gray-900 border border-gray-800 rounded-lg px-4 py-2.5 text-sm font-mono text-gray-100 placeholder:text-gray-600 focus:outline-none focus:border-green-400/50 transition-colors"
          />
        </FieldGroup>

        {/* Bio */}
        <FieldGroup label="bio">
          <textarea
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            placeholder="Tell collaborators about yourself..."
            rows={3}
            className="w-full bg-gray-900 border border-gray-800 rounded-lg px-4 py-2.5 text-sm font-mono text-gray-100 placeholder:text-gray-600 focus:outline-none focus:border-green-400/50 transition-colors resize-none"
          />
        </FieldGroup>

        {/* Skills */}
        <FieldGroup label="skills" hint="comma-separated">
          <input
            type="text"
            value={skills}
            onChange={(e) => setSkills(e.target.value)}
            placeholder="react, python, figma, ux-research"
            className="w-full bg-gray-900 border border-gray-800 rounded-lg px-4 py-2.5 text-sm font-mono text-gray-100 placeholder:text-gray-600 focus:outline-none focus:border-green-400/50 transition-colors"
          />
        </FieldGroup>

        {/* Availability */}
        <FieldGroup label="availability">
          <input
            type="text"
            value={availability}
            onChange={(e) => setAvailability(e.target.value)}
            placeholder="e.g. 10 hrs/week, evenings & weekends"
            className="w-full bg-gray-900 border border-gray-800 rounded-lg px-4 py-2.5 text-sm font-mono text-gray-100 placeholder:text-gray-600 focus:outline-none focus:border-green-400/50 transition-colors"
          />
        </FieldGroup>

        {/* Interested Project Types */}
        <FieldGroup label="interested_project_types">
          <div className="flex flex-wrap gap-3">
            {PROJECT_TYPES.map((pt) => (
              <label
                key={pt.value}
                className="flex items-center gap-2 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={interestedTypes.includes(pt.value)}
                  onChange={() =>
                    toggleCheckbox(pt.value, interestedTypes, setInterestedTypes)
                  }
                  className="w-4 h-4 rounded border-gray-700 bg-gray-900 text-green-400 focus:ring-green-400/30 focus:ring-offset-0"
                />
                <span className="text-sm font-mono text-gray-300">
                  {pt.label}
                </span>
              </label>
            ))}
          </div>
        </FieldGroup>

        {/* Preferred Roles */}
        <FieldGroup label="preferred_roles">
          <div className="flex flex-wrap gap-3">
            {PREFERRED_ROLES.map((r) => (
              <label
                key={r.value}
                className="flex items-center gap-2 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={preferredRoles.includes(r.value)}
                  onChange={() =>
                    toggleCheckbox(r.value, preferredRoles, setPreferredRoles)
                  }
                  className="w-4 h-4 rounded border-gray-700 bg-gray-900 text-green-400 focus:ring-green-400/30 focus:ring-offset-0"
                />
                <span className="text-sm font-mono text-gray-300">
                  {r.label}
                </span>
              </label>
            ))}
          </div>
        </FieldGroup>

        {/* External Links */}
        <FieldGroup label="external_links" hint="one per line">
          <textarea
            value={externalLinks}
            onChange={(e) => setExternalLinks(e.target.value)}
            placeholder={"https://github.com/username\nhttps://linkedin.com/in/username"}
            rows={3}
            className="w-full bg-gray-900 border border-gray-800 rounded-lg px-4 py-2.5 text-sm font-mono text-gray-100 placeholder:text-gray-600 focus:outline-none focus:border-green-400/50 transition-colors resize-none"
          />
        </FieldGroup>

        {/* Message */}
        {message && (
          <div
            className={`rounded-lg border px-4 py-2.5 text-sm font-mono ${
              message.type === "success"
                ? "border-green-400/30 bg-green-400/5 text-green-400"
                : "border-red-400/30 bg-red-400/5 text-red-400"
            }`}
          >
            {message.text}
          </div>
        )}

        {/* Save Button */}
        <button
          type="submit"
          disabled={saving}
          className="w-full rounded-lg bg-green-400/10 border border-green-400/30 px-4 py-2.5 text-sm font-mono text-green-400 hover:bg-green-400/20 hover:border-green-400/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {saving ? "saving..." : "$ save profile"}
        </button>
      </form>
    </div>
  );
}

function FieldGroup({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-xs font-mono text-cyan-400 uppercase tracking-wider mb-2">
        {label}
        {hint && (
          <span className="text-gray-600 normal-case tracking-normal ml-2">
            ({hint})
          </span>
        )}
      </label>
      {children}
    </div>
  );
}
