"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useRegister } from "@/hooks/use-auth";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [entryIntent, setEntryIntent] = useState<
    "founder" | "collaborator" | "both"
  >("both");

  const register = useRegister();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    register.mutate({
      email,
      password,
      display_name: displayName,
      entry_intent: entryIntent,
    });
  }

  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-6">Register</h1>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="border rounded-lg px-3 py-2"
        />
        <input
          type="password"
          placeholder="Password (min 8 characters)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
          className="border rounded-lg px-3 py-2"
        />
        <input
          type="text"
          placeholder="Display name"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          required
          className="border rounded-lg px-3 py-2"
        />
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium">I want to:</label>
          <div className="flex gap-3">
            {[
              { value: "founder" as const, label: "Initiate projects" },
              { value: "collaborator" as const, label: "Join projects" },
              { value: "both" as const, label: "Both" },
            ].map((opt) => (
              <label key={opt.value} className="flex items-center gap-1.5 text-sm">
                <input
                  type="radio"
                  name="intent"
                  value={opt.value}
                  checked={entryIntent === opt.value}
                  onChange={() => setEntryIntent(opt.value)}
                />
                {opt.label}
              </label>
            ))}
          </div>
        </div>

        {register.error && (
          <p className="text-sm text-red-600">
            {(register.error as Error).message}
          </p>
        )}

        <p className="text-xs text-gray-500">
          By creating an account, you agree to the{" "}
          <Link href="/terms" className="text-cyan-400 hover:underline">Terms of Service</Link>
          {" "}and acknowledge the{" "}
          <Link href="/privacy" className="text-cyan-400 hover:underline">Privacy Policy</Link>.
        </p>

        <Button type="submit" disabled={register.isPending}>
          {register.isPending ? "Registering..." : "Register"}
        </Button>
      </form>
      <p className="mt-4 text-sm text-muted-foreground">
        Already have an account?{" "}
        <Link href="/login" className="underline">
          Log in
        </Link>
      </p>
    </div>
  );
}
