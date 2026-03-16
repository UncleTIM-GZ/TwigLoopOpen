import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Terms of Service | Twig Loop",
  description: "Twig Loop terms of service",
};

export default function TermsPage() {
  return (
    <div className="space-y-12 max-w-3xl">
      {/* Header */}
      <section>
        <h1 className="font-mono text-sm text-gray-500 mb-4">
          $ cat terms-of-service.txt
        </h1>
        <h2 className="font-mono text-2xl font-bold text-green-400 mb-2">
          Terms of Service
        </h2>
        <p className="font-mono text-xs text-gray-600">
          Effective: March 16, 2026
        </p>
      </section>

      {/* Beta Service */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Beta Service
        </h2>
        <div className="border border-yellow-400/30 p-5">
          <p className="font-mono text-xs text-yellow-400 mb-2">
            IMPORTANT
          </p>
          <p className="font-mono text-sm text-gray-400 leading-relaxed">
            Twig Loop is currently in Public Beta. The service is provided
            as-is, with no guarantee of uptime, availability, or data
            persistence. Features may change, be removed, or be temporarily
            unavailable without prior notice.
          </p>
        </div>
      </section>

      {/* Your Content */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Your Content
        </h2>
        <div className="space-y-2 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            You retain ownership of all content you create on Twig Loop,
            including project proposals, work package descriptions, and task
            card content. By posting content, you grant Twig Loop a
            non-exclusive license to display it within the platform for
            collaboration purposes.
          </p>
        </div>
      </section>

      {/* Work Units */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Work Units (EWU / RWU / SWU)
        </h2>
        <div className="space-y-2 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            EWU (Effort Work Units), RWU (Reward Work Units), and SWU (Sponsor
            Work Units) are internal metrics used to estimate task complexity
            and track collaboration effort. They are{" "}
            <span className="text-yellow-400">not currency</span>, do not
            represent monetary value, and cannot be exchanged, transferred, or
            redeemed outside the platform.
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
            Verifiable Credentials (VCs) issued by Twig Loop are beta features.
            They are experimental proof-of-work records, not legal
            certifications, professional licenses, or official qualifications.
            Third parties are not obligated to recognize them.
          </p>
        </div>
      </section>

      {/* Acceptable Use */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Acceptable Use
        </h2>
        <div className="border border-gray-800 p-5 space-y-2">
          {[
            "Do not use the platform for illegal activities",
            "Do not attempt to abuse, exploit, or disrupt the service",
            "Do not misrepresent your identity or qualifications",
            "Do not scrape or bulk-download platform data",
            "Do not submit false progress signals or fabricate contributions",
          ].map((item, i) => (
            <p key={i} className="font-mono text-xs text-gray-400">
              <span className="text-gray-600 mr-2">-</span>
              {item}
            </p>
          ))}
        </div>
      </section>

      {/* No Warranty */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Disclaimer & No Warranty
        </h2>
        <div className="space-y-2 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            The service is provided &quot;as-is&quot; and &quot;as
            available&quot; without warranty of any kind, express or implied.
            Twig Loop does not guarantee that the service will be
            uninterrupted, secure, or error-free.
          </p>
        </div>
      </section>

      {/* Contact */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Contact
        </h2>
        <div className="space-y-2 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            Questions about these terms? Contact us at{" "}
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
