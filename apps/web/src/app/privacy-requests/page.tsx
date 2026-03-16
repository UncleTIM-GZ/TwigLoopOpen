import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Privacy Requests | Twig Loop",
  description: "Submit privacy-related requests to Twig Loop",
};

export default function PrivacyRequestsPage() {
  return (
    <div className="space-y-12 max-w-3xl">
      {/* Header */}
      <section>
        <h1 className="font-mono text-sm text-gray-500 mb-4">
          $ cat privacy-requests.txt
        </h1>
        <h2 className="font-mono text-2xl font-bold text-green-400 mb-2">
          Privacy Requests
        </h2>
      </section>

      {/* How to Submit */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## How to Submit a Request
        </h2>
        <div className="space-y-2 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            To exercise your privacy rights (access, correction, or deletion of
            your personal data), send an email to{" "}
            <a
              href="mailto:privacy@twigloop.tech"
              className="text-cyan-400 hover:underline"
            >
              privacy@twigloop.tech
            </a>
            .
          </p>
        </div>
      </section>

      {/* What to Include */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## What to Include
        </h2>
        <div className="border border-gray-800 p-5 space-y-2">
          {[
            "Your registered email address",
            "The type of request: access, correction, or deletion",
            "For correction requests: specify what data needs to be updated",
            "For access requests: we will provide a copy of your stored data",
          ].map((item, i) => (
            <p key={i} className="font-mono text-xs text-gray-400">
              <span className="text-cyan-400 mr-2">{i + 1}.</span>
              {item}
            </p>
          ))}
        </div>
      </section>

      {/* Available Requests */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Available Request Types
        </h2>
        <div className="space-y-4">
          <div className="border border-cyan-400/30 p-4">
            <h3 className="font-mono text-sm text-cyan-400 mb-2">
              Data Access
            </h3>
            <p className="font-mono text-xs text-gray-400 leading-relaxed">
              Request a copy of all personal data we hold about you, including
              account information, project content, and usage logs.
            </p>
          </div>
          <div className="border border-cyan-400/30 p-4">
            <h3 className="font-mono text-sm text-cyan-400 mb-2">
              Data Correction
            </h3>
            <p className="font-mono text-xs text-gray-400 leading-relaxed">
              Request correction of inaccurate or incomplete personal data.
              Specify the data fields that need updating.
            </p>
          </div>
          <div className="border border-cyan-400/30 p-4">
            <h3 className="font-mono text-sm text-cyan-400 mb-2">
              Data Deletion
            </h3>
            <p className="font-mono text-xs text-gray-400 leading-relaxed">
              Request deletion of your account and all associated personal
              data. This action is irreversible. Project content you
              contributed may be anonymized rather than deleted to preserve
              collaboration history.
            </p>
          </div>
        </div>
      </section>

      {/* Response Time */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Response Time
        </h2>
        <div className="space-y-2 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            We will respond to your request within 30 days. Verification will
            be conducted via your registered email address.
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
