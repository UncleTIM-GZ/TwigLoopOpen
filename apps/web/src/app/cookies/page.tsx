import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Cookie Notice | Twig Loop",
  description: "Twig Loop cookie notice",
};

export default function CookiesPage() {
  return (
    <div className="space-y-12 max-w-3xl">
      {/* Header */}
      <section>
        <h1 className="font-mono text-sm text-gray-500 mb-4">
          $ cat cookie-notice.txt
        </h1>
        <h2 className="font-mono text-2xl font-bold text-green-400 mb-2">
          Cookie Notice
        </h2>
        <p className="font-mono text-xs text-gray-600">
          Effective: March 16, 2026
        </p>
      </section>

      {/* Overview */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Overview
        </h2>
        <div className="space-y-2 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            Twig Loop uses essential cookies only. We do not use tracking,
            analytics, or advertising cookies. Your browsing behavior is not
            shared with any third-party advertisers.
          </p>
        </div>
      </section>

      {/* Cookies We Use */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Cookies We Use
        </h2>
        <div className="space-y-4">
          <div className="border border-cyan-400/30 p-4">
            <h3 className="font-mono text-sm text-cyan-400 mb-2">
              Authentication Session
            </h3>
            <p className="font-mono text-xs text-gray-400 leading-relaxed">
              A session cookie is set when you log in. It maintains your
              authenticated state across page navigations. This cookie is
              httpOnly, secure, and expires when your session ends or after a
              set timeout.
            </p>
          </div>
          <div className="border border-cyan-400/30 p-4">
            <h3 className="font-mono text-sm text-cyan-400 mb-2">
              Cloudflare Security
            </h3>
            <p className="font-mono text-xs text-gray-400 leading-relaxed">
              Cloudflare may set cookies for DDoS protection and bot detection
              (e.g., __cf_bm). These are essential security cookies managed by
              Cloudflare and are necessary for the platform to function
              properly.
            </p>
          </div>
        </div>
      </section>

      {/* What We Don't Use */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## What We Don&apos;t Use
        </h2>
        <div className="border border-gray-800 p-5 space-y-2">
          {[
            "No Google Analytics or similar tracking",
            "No advertising cookies or pixels",
            "No social media tracking cookies",
            "No cross-site tracking of any kind",
          ].map((item, i) => (
            <p key={i} className="font-mono text-xs text-gray-400">
              <span className="text-green-400 mr-2">x</span>
              {item}
            </p>
          ))}
        </div>
      </section>

      {/* Managing Cookies */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Managing Cookies
        </h2>
        <div className="space-y-2 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            You can manage cookies through your browser settings. Disabling
            essential cookies may prevent you from logging in or using
            authenticated features.
          </p>
        </div>
      </section>

      {/* Back */}
      <section className="pb-8">
        <Link
          href="/"
          className="font-mono text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
        >
          {"< "} Back to Home
        </Link>
      </section>
    </div>
  );
}
