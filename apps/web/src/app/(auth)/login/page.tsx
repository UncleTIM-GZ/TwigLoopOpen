"use client";

import { useState } from "react";
import { useLogin } from "@/hooks/use-auth";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const login = useLogin();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    login.mutate({ email, password });
  }

  return (
    <div className="max-w-md mx-auto">
      <div className="bg-gray-950 rounded-xl p-6 md:p-8 text-gray-100">
        {/* Header */}
        <div className="border-b border-gray-800 pb-6 mb-6">
          <h1 className="text-2xl font-bold font-mono text-green-400 mb-2">
            $ login
          </h1>
          <p className="text-sm text-gray-400 font-mono leading-relaxed">
            Sign in to your Twig Loop account.
            <br />
            This portal is for MCP-registered users.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <div>
            <label className="block text-xs font-mono text-cyan-400 uppercase tracking-wider mb-2">
              email
            </label>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full bg-gray-900 border border-gray-800 rounded-lg px-4 py-2.5 text-sm font-mono text-gray-100 placeholder:text-gray-600 focus:outline-none focus:border-green-400/50 transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-mono text-cyan-400 uppercase tracking-wider mb-2">
              password
            </label>
            <input
              type="password"
              placeholder="********"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full bg-gray-900 border border-gray-800 rounded-lg px-4 py-2.5 text-sm font-mono text-gray-100 placeholder:text-gray-600 focus:outline-none focus:border-green-400/50 transition-colors"
            />
          </div>

          {login.error && (
            <div className="rounded-lg border border-red-400/30 bg-red-400/5 px-4 py-2.5 text-sm font-mono text-red-400">
              {(login.error as Error).message}
            </div>
          )}

          <button
            type="submit"
            disabled={login.isPending}
            className="w-full rounded-lg bg-green-400/10 border border-green-400/30 px-4 py-2.5 text-sm font-mono text-green-400 hover:bg-green-400/20 hover:border-green-400/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {login.isPending ? "authenticating..." : "$ login"}
          </button>
        </form>

        {/* MCP Notice */}
        <div className="mt-6 pt-6 border-t border-gray-800">
          <p className="text-xs text-gray-500 font-mono leading-relaxed">
            Not registered?
            <br />
            Accounts are created via MCP tools.
            <br />
            <span className="text-gray-600">
              Use your MCP client to run{" "}
              <span className="text-cyan-400/70">register_user</span> first.
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}
