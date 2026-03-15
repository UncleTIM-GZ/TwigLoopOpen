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
  { value: "general", label: "一般项目", desc: "自由发起的开发型项目" },
  { value: "public_benefit", label: "公益项目", desc: "面向弱势群体的公益项目" },
  { value: "recruitment", label: "招募项目", desc: "有激励的招募型项目" },
];

const FOUNDER_TYPES: { value: FounderType; label: string }[] = [
  { value: "ordinary", label: "普通人" },
  { value: "help_seeker", label: "需要帮助的人或机构" },
  { value: "contributor", label: "贡献者" },
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
      <h1 className="text-2xl font-bold mb-6">发起项目</h1>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          create.mutate();
        }}
        className="flex flex-col gap-6"
      >
        <div>
          <label className="text-sm font-medium block mb-2">项目类型</label>
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
          <label className="text-sm font-medium block mb-2">发起者身份</label>
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
          placeholder="项目标题"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          className="border rounded-lg px-3 py-2"
        />
        <textarea
          placeholder="项目描述"
          value={summary}
          onChange={(e) => setSummary(e.target.value)}
          required
          rows={4}
          className="border rounded-lg px-3 py-2"
        />
        <input
          type="text"
          placeholder="面向对象（可选）"
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
          {create.isPending ? "创建中..." : "创建项目"}
        </Button>
      </form>
    </div>
  );
}
