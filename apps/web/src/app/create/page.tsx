"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/api-client";
import type { ApiResponse, ProjectResponse } from "@/types/api";

type ProjectType = "general" | "public_benefit" | "recruitment";
type FounderType = "ordinary" | "help_seeker" | "contributor";

const PROJECT_TYPES: { value: ProjectType; label: string; desc: string }[] = [
  { value: "general", label: "General Project", desc: "Freely initiated development projects" },
  { value: "public_benefit", label: "Public Benefit Project", desc: "Projects serving underserved communities" },
  { value: "recruitment", label: "Recruitment Project", desc: "Incentivized recruitment projects" },
];

const FOUNDER_TYPES: { value: FounderType; label: string }[] = [
  { value: "ordinary", label: "Individual" },
  { value: "help_seeker", label: "Help seeker / Organization" },
  { value: "contributor", label: "Contributor" },
];

export default function CreateProjectPage() {
  const router = useRouter();
  const [projectType, setProjectType] = useState<ProjectType>("general");
  const [founderType, setFounderType] = useState<FounderType>("ordinary");
  const [title, setTitle] = useState("");
  const [summary, setSummary] = useState("");
  const [targetUsers, setTargetUsers] = useState("");

  const create = useMutation({
    mutationFn: () =>
      apiClient<ApiResponse<ProjectResponse>>("/api/v1/projects/", {
        method: "POST",
        body: JSON.stringify({
          project_type: projectType,
          founder_type: founderType,
          title,
          summary,
          target_users: targetUsers || undefined,
          created_via: "web",
        }),
      }),
    onSuccess: (res) => {
      if (res.data) router.push(`/projects/${res.data.project_id}`);
    },
  });

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Create Project</h1>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          create.mutate();
        }}
        className="flex flex-col gap-6"
      >
        <div>
          <label className="text-sm font-medium block mb-2">Project Type</label>
          <div className="grid gap-2">
            {PROJECT_TYPES.map((t) => (
              <label
                key={t.value}
                className={`border rounded-lg p-3 cursor-pointer ${
                  projectType === t.value ? "border-primary bg-primary/5" : ""
                }`}
              >
                <input
                  type="radio"
                  name="projectType"
                  value={t.value}
                  checked={projectType === t.value}
                  onChange={() => setProjectType(t.value)}
                  className="sr-only"
                />
                <span className="font-medium">{t.label}</span>
                <span className="text-sm text-muted-foreground ml-2">
                  {t.desc}
                </span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="text-sm font-medium block mb-2">Founder Type</label>
          <div className="flex gap-3">
            {FOUNDER_TYPES.map((f) => (
              <label key={f.value} className="flex items-center gap-1.5 text-sm">
                <input
                  type="radio"
                  name="founderType"
                  checked={founderType === f.value}
                  onChange={() => setFounderType(f.value)}
                />
                {f.label}
              </label>
            ))}
          </div>
        </div>

        <input
          type="text"
          placeholder="Project title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          className="border rounded-lg px-3 py-2"
        />
        <textarea
          placeholder="Project description"
          value={summary}
          onChange={(e) => setSummary(e.target.value)}
          required
          rows={4}
          className="border rounded-lg px-3 py-2"
        />
        <input
          type="text"
          placeholder="Target audience (optional)"
          value={targetUsers}
          onChange={(e) => setTargetUsers(e.target.value)}
          className="border rounded-lg px-3 py-2"
        />

        {create.error && (
          <p className="text-sm text-red-600">
            {(create.error as Error).message}
          </p>
        )}

        <Button type="submit" disabled={create.isPending}>
          {create.isPending ? "Creating..." : "Create Project"}
        </Button>
      </form>
    </div>
  );
}
