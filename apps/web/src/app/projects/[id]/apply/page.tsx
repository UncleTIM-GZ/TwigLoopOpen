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
      <h1 className="text-2xl font-bold mb-6">Apply to Project</h1>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          apply.mutate();
        }}
        className="flex flex-col gap-4"
      >
        <div>
          <label className="text-sm font-medium block mb-1">Seat Preference</label>
          <div className="flex gap-4">
            {[
              { v: "growth" as const, l: "Growth Seat" },
              { v: "formal" as const, l: "Formal Seat" },
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
          placeholder="Intended role"
          value={role}
          onChange={(e) => setRole(e.target.value)}
          required
          className="border rounded-lg px-3 py-2"
        />
        <textarea
          placeholder="Motivation (optional)"
          value={motivation}
          onChange={(e) => setMotivation(e.target.value)}
          rows={3}
          className="border rounded-lg px-3 py-2"
        />
        <input
          type="text"
          placeholder="Availability (optional)"
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
          {apply.isPending ? "Submitting..." : "Submit Application"}
        </Button>
      </form>
    </div>
  );
}
