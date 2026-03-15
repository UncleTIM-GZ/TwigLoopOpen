"use client";

import Link from "next/link";
import { useMe, useLogout } from "@/hooks/use-auth";

const NAV_LINKS = [
  { href: "/", label: "Home" },
  { href: "/projects", label: "Projects" },
  { href: "/status", label: "Status" },
  { href: "/create/public-benefit", label: "Public Benefit" },
  { href: "/help", label: "Help" },
];

export function NavBar() {
  const { data: meRes } = useMe();
  const logout = useLogout();
  const isLoggedIn = meRes?.data?.actor != null;
  const displayName = meRes?.data?.actor?.display_name;

  return (
    <nav className="border-b border-gray-800 px-6 py-3 flex items-center justify-between bg-gray-950">
      <div className="flex items-center gap-6">
        <Link href="/" className="font-mono text-lg font-bold text-green-400">
          twig-loop
        </Link>
        {NAV_LINKS.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="font-mono text-xs text-gray-400 hover:text-green-400 transition-colors"
          >
            {link.label}
          </Link>
        ))}
      </div>
      <div className="flex items-center gap-4">
        {isLoggedIn ? (
          <>
            <Link
              href="/dashboard"
              className="font-mono text-xs text-gray-400 hover:text-green-400 transition-colors"
            >
              Dashboard
            </Link>
            <span className="font-mono text-xs text-gray-500">
              {displayName}
            </span>
            <button
              onClick={logout}
              className="font-mono text-xs text-gray-500 hover:text-red-400 transition-colors"
            >
              logout
            </button>
          </>
        ) : (
          <>
            <Link
              href="/login"
              className="font-mono text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
            >
              MCP Login
            </Link>
            <Link
              href="/register"
              className="font-mono text-xs px-3 py-1 border border-green-400/40 text-green-400 hover:bg-green-400/10 transition-colors"
            >
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
