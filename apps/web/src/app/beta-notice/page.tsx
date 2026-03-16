import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Beta Notice | Twig Loop",
  description: "Twig Loop public beta notice and disclaimers",
};

export default function BetaNoticePage() {
  return (
    <div className="space-y-12 max-w-3xl">
      {/* Header */}
      <section>
        <h1 className="font-mono text-sm text-gray-500 mb-4">
          $ cat beta-notice.txt
        </h1>
        <h2 className="font-mono text-2xl font-bold text-green-400 mb-2">
          Beta Notice
        </h2>
        <div className="inline-block mt-2">
          <span className="font-mono text-xs px-3 py-1 border border-green-400/40 bg-green-400/10 text-green-400">
            Public Beta
          </span>
        </div>
      </section>

      {/* Current Status */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Current Status
        </h2>
        <div className="space-y-2 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            Twig Loop is currently in Public Beta. This means the platform is
            open for registration and use, but features, APIs, and data
            structures may change as we iterate toward a stable release.
          </p>
        </div>
      </section>

      {/* What Beta Means */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## What Beta Means
        </h2>
        <div className="border border-yellow-400/30 p-5 space-y-2">
          {[
            "Features may change, be added, or be removed without prior notice",
            "Data may be reset with advance notice during major updates",
            "No guarantee of uptime or service availability",
            "Performance may vary as we optimize infrastructure",
          ].map((item, i) => (
            <p key={i} className="font-mono text-xs text-gray-400">
              <span className="text-yellow-400 mr-2">!</span>
              {item}
            </p>
          ))}
        </div>
      </section>

      {/* Work Units Disclaimer */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Work Units (EWU / RWU / SWU)
        </h2>
        <div className="space-y-2 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            EWU, RWU, and SWU are internal effort-tracking metrics. During
            beta, they carry{" "}
            <span className="text-yellow-400">no financial value</span>.
            Calculation formulas and weightings may be adjusted as the system
            matures.
          </p>
        </div>
      </section>

      {/* Verifiable Credentials */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Verifiable Credentials
        </h2>
        <div className="space-y-2 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            Verifiable Credentials (VCs) issued during beta are experimental.
            They serve as proof-of-participation records but are not official
            certifications. Their format and validity rules may change before
            the stable release.
          </p>
        </div>
      </section>

      {/* Feedback */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Feedback
        </h2>
        <div className="space-y-2 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            We welcome feedback during the beta period. Your input directly
            shapes the platform. Reach out at{" "}
            <a
              href="mailto:hello@twigloop.tech"
              className="text-cyan-400 hover:underline"
            >
              hello@twigloop.tech
            </a>
            .
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
