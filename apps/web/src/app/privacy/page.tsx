import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Privacy Policy | Twig Loop",
  description: "Twig Loop privacy policy",
};

export default function PrivacyPage() {
  return (
    <div className="space-y-12 max-w-3xl">
      {/* Header */}
      <section>
        <h1 className="font-mono text-sm text-gray-500 mb-4">
          $ cat privacy-policy.txt
        </h1>
        <h2 className="font-mono text-2xl font-bold text-green-400 mb-2">
          Privacy Policy
        </h2>
        <p className="font-mono text-xs text-gray-600">
          Effective: March 16, 2026
        </p>
      </section>

      {/* Operator */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Operator
        </h2>
        <div className="space-y-2 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            Twig Loop is operated by Timothy Ou as a solo-operated platform.
          </p>
          <p>
            Contact:{" "}
            <a
              href="mailto:privacy@twigloop.tech"
              className="text-cyan-400 hover:underline"
            >
              privacy@twigloop.tech
            </a>
          </p>
        </div>
      </section>

      {/* Data We Collect */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Data We Collect
        </h2>
        <div className="border border-gray-800 p-5 space-y-2">
          {[
            "Email address (for authentication)",
            "Display name and bio (for your public profile)",
            "Project content you create (proposals, work packages, task cards)",
            "Usage logs (page views, API requests, timestamps)",
          ].map((item, i) => (
            <p key={i} className="font-mono text-xs text-gray-400">
              <span className="text-gray-600 mr-2">-</span>
              {item}
            </p>
          ))}
        </div>
      </section>

      {/* How We Store Data */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## How We Store Data
        </h2>
        <div className="space-y-2 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            Data is stored on Railway (US-based infrastructure) using PostgreSQL
            for application data and Redis for session management. All
            connections use TLS encryption.
          </p>
        </div>
      </section>

      {/* Third-Party Services */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Third-Party Services
        </h2>
        <div className="border border-gray-800 p-5 space-y-2">
          {[
            "Cloudflare — CDN, DDoS protection, security cookies",
            "Railway — Application hosting and database infrastructure",
            "GitHub — Source sync for progress verification (optional, user-initiated)",
          ].map((item, i) => (
            <p key={i} className="font-mono text-xs text-gray-400">
              <span className="text-gray-600 mr-2">-</span>
              {item}
            </p>
          ))}
        </div>
      </section>

      {/* Cookies */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Cookies
        </h2>
        <div className="space-y-2 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            We use essential cookies only for authentication sessions. No
            tracking or advertising cookies are used. See our{" "}
            <Link
              href="/cookies"
              className="text-cyan-400 hover:underline"
            >
              Cookie Notice
            </Link>{" "}
            for details.
          </p>
        </div>
      </section>

      {/* Your Rights */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Your Rights
        </h2>
        <div className="border border-gray-800 p-5 space-y-2">
          {[
            "Access — Request a copy of your personal data",
            "Correction — Request correction of inaccurate data",
            "Deletion — Request deletion of your account and data",
          ].map((item, i) => (
            <p key={i} className="font-mono text-xs text-gray-400">
              <span className="text-gray-600 mr-2">-</span>
              {item}
            </p>
          ))}
          <p className="font-mono text-xs text-gray-500 mt-3">
            To exercise these rights, email{" "}
            <a
              href="mailto:privacy@twigloop.tech"
              className="text-cyan-400 hover:underline"
            >
              privacy@twigloop.tech
            </a>{" "}
            or visit{" "}
            <Link
              href="/privacy-requests"
              className="text-cyan-400 hover:underline"
            >
              Privacy Requests
            </Link>
            .
          </p>
        </div>
      </section>

      {/* Children */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Children
        </h2>
        <div className="space-y-2 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            Twig Loop is not directed at individuals under 16 years of age. We
            do not knowingly collect personal data from children. If you believe
            a child has provided us data, contact us for deletion.
          </p>
        </div>
      </section>

      {/* International Data Transfer */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## International Data Transfer
        </h2>
        <div className="space-y-2 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            Your data is processed and stored in the United States. By using
            Twig Loop, you consent to the transfer of your data to the US.
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
