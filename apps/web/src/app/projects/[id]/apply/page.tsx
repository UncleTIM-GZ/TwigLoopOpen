"use client";

import { use, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/api-client";
import type { ApiResponse, ApplicationResponse } from "@/types/api";

export default function ApplyPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const [seatPref, setSeatPref] = useState<"growth" | "formal">("growth");
  const [role, setRole] = useState("");
  const [motivation, setMotivation] = useState("");
  const [availability, setAvailability] = useState("");

  const apply = useMutation({
    mutationFn: () =>
      apiClient<ApiResponse<ApplicationResponse>>(
        `/api/v1/projects/${id}/applications`,
        {
          method: "POST",
          body: JSON.stringify({
            seat_preference: seatPref,
            intended_role: role,
            motivation: motivation || undefined,
            availability: availability || undefined,
          }),
        },
      ),
    onSuccess: () => router.push("/dashboard"),
  });

  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-6">申请加入项目</h1>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          apply.mutate();
        }}
        className="flex flex-col gap-4"
      >
        <div>
          <label className="text-sm font-medium block mb-1">席位偏好</label>
          <div className="flex gap-4">
            {[
              { v: "growth" as const, l: "成长席位" },
              { v: "formal" as const, l: "正式席位" },
            ].map((o) => (
              <label key={o.v} className="flex items-center gap-1.5 text-sm">
                <input
                  type="radio"
                  name="seat"
                  checked={seatPref === o.v}
                  onChange={() => setSeatPref(o.v)}
                />
                {o.l}
              </label>
            ))}
          </div>
        </div>

        <input
          type="text"
          placeholder="希望承担的角色"
          value={role}
          onChange={(e) => setRole(e.target.value)}
          required
          className="border rounded-lg px-3 py-2"
        />
        <textarea
          placeholder="申请动机（可选）"
          value={motivation}
          onChange={(e) => setMotivation(e.target.value)}
          rows={3}
          className="border rounded-lg px-3 py-2"
        />
        <input
          type="text"
          placeholder="可投入时间（可选）"
          value={availability}
          onChange={(e) => setAvailability(e.target.value)}
          className="border rounded-lg px-3 py-2"
        />

        {apply.error && (
          <p className="text-sm text-red-600">
            {(apply.error as Error).message}
          </p>
        )}

        <Button type="submit" disabled={apply.isPending}>
          {apply.isPending ? "提交中..." : "提交申请"}
        </Button>
      </form>
    </div>
  );
}
