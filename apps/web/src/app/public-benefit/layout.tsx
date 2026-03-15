"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/public-benefit/requests", label: "My Requests" },
  { href: "/public-benefit/apply", label: "New Request" },
  { href: "#", label: "Organization Profile" },
  { href: "#", label: "Help" },
] as const;

export default function PublicBenefitLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const isAuthPage =
    pathname === "/public-benefit/login" ||
    pathname === "/public-benefit/register";

  return (
    <div className="min-h-screen bg-gray-950 text-gray-200">
      {/* Top bar */}
      <header className="border-b border-gray-800 px-6 py-3 flex items-center justify-between">
        <Link
          href="/public-benefit/requests"
          className="font-mono text-lg font-bold text-green-400 tracking-tight"
        >
          Twig Loop &middot; Public Benefit
        </Link>

        {!isAuthPage && (
          <div className="flex items-center gap-4">
            <Link
              href="/public-benefit/login"
              className="text-sm text-gray-400 hover:text-green-400 transition-colors"
            >
              Logout
            </Link>
          </div>
        )}
      </header>

      <div className="flex">
        {/* Sidebar nav -- hidden on auth pages */}
        {!isAuthPage && (
          <nav className="w-52 shrink-0 border-r border-gray-800 min-h-[calc(100vh-49px)] py-6 px-4">
            <ul className="flex flex-col gap-1">
              {NAV_ITEMS.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className={cn(
                      "block rounded-md px-3 py-2 text-sm transition-colors",
                      pathname === item.href
                        ? "bg-gray-800 text-green-400"
                        : "text-gray-400 hover:bg-gray-900 hover:text-gray-200",
                    )}
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        )}

        {/* Main content */}
        <main className="flex-1 px-8 py-8 max-w-4xl">{children}</main>
      </div>
    </div>
  );
}
