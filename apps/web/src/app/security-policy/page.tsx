import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Security Policy | Twig Loop",
  description: "Twig Loop security policy and vulnerability reporting",
};

export default function SecurityPolicyPage() {
  return (
    <div className="space-y-12 max-w-3xl">
      {/* Header */}
      <section>
        <h1 className="font-mono text-sm text-gray-500 mb-4">
          $ cat security-policy.txt
        </h1>
        <h2 className="font-mono text-2xl font-bold text-green-400 mb-2">
          Security Policy
        </h2>
        <p className="font-mono text-xs text-gray-600">
          Effective: March 16, 2026
        </p>
      </section>

      {/* Reporting Vulnerabilities */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Reporting Vulnerabilities
        </h2>
        <div className="border border-yellow-400/30 p-5">
          <p className="font-mono text-xs text-yellow-400 mb-2">
            IMPORTANT
          </p>
          <div className="space-y-2 font-mono text-sm text-gray-400 leading-relaxed">
            <p>
              If you discover a security vulnerability, please report it
              privately to{" "}
              <a
                href="mailto:security@twigloop.tech"
                className="text-cyan-400 hover:underline"
              >
                security@twigloop.tech
              </a>
              . Do not open public GitHub issues for security vulnerabilities.
            </p>
            <p>
              We will acknowledge your report within 48 hours and work to
              resolve verified issues as quickly as possible.
            </p>
          </div>
        </div>
      </section>

      {/* Security Measures */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Security Measures
        </h2>
        <div className="border border-gray-800 p-5 space-y-2">
          {[
            "HTTPS enforced on all connections",
            "Passwords hashed with bcrypt",
            "Session cookies are httpOnly and secure",
            "Rate limiting on authentication endpoints",
            "Input validation on all API boundaries",
            "SQL injection prevention via parameterized queries",
          ].map((item, i) => (
            <p key={i} className="font-mono text-xs text-gray-400">
              <span className="text-green-400 mr-2">[+]</span>
              {item}
            </p>
          ))}
        </div>
      </section>

      {/* Beta Disclaimer */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Beta Disclaimer
        </h2>
        <div className="space-y-2 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            Twig Loop is in Public Beta. While we implement industry-standard
            security practices, we do not make &quot;bank-grade&quot; or
            &quot;military-grade&quot; security claims. The platform is
            continuously improving its security posture.
          </p>
        </div>
      </section>

      {/* Bug Bounty */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Bug Bounty
        </h2>
        <div className="space-y-2 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            We do not currently operate a formal bug bounty program. We
            appreciate responsible disclosure and will credit reporters (with
            permission) in our security acknowledgments.
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
