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
      <h1 className="text-2xl font-bold mb-6">注册</h1>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <input
          type="email"
          placeholder="邮箱"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="border rounded-lg px-3 py-2"
        />
        <input
          type="password"
          placeholder="密码（至少8位）"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
          className="border rounded-lg px-3 py-2"
        />
        <input
          type="text"
          placeholder="显示名"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          required
          className="border rounded-lg px-3 py-2"
        />
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium">我想要：</label>
          <div className="flex gap-3">
            {[
              { value: "founder" as const, label: "发起项目" },
              { value: "collaborator" as const, label: "参与项目" },
              { value: "both" as const, label: "两者都可" },
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

        <Button type="submit" disabled={register.isPending}>
          {register.isPending ? "注册中..." : "注册"}
        </Button>
      </form>
      <p className="mt-4 text-sm text-muted-foreground">
        已有账号？{" "}
        <Link href="/login" className="underline">
          登录
        </Link>
      </p>
    </div>
  );
}
