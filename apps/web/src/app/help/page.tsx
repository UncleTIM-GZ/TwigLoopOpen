import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Help | Twig Loop",
  description: "Twig Loop help center and documentation",
};

const FAQ_ITEMS = [
  {
    q: "How do I create a project?",
    a: 'Register an account, then click "Initiate Project" from the navigation. Fill in the project details, and the platform will help structure it into work packages and task cards.',
  },
  {
    q: "How does collaboration matching work?",
    a: "Each project has open seats with specific roles (e.g., backend developer, designer). Contributors browse projects, find matching seats, and submit applications with their intended role and motivation.",
  },
  {
    q: "What are EWU, RWU, and SWU?",
    a: "EWU (Effort Work Units) is the base unit measuring task complexity — calculated from task type, complexity, criticality, collaboration complexity, and risk level. RWU (Reward Work Units) = EWU × 1.2, applies only to recruitment projects. SWU (Sponsor Work Units) = EWU × 1.0 (v1), applies to sponsored public-benefit projects. Work packages and projects aggregate EWU/RWU/SWU from their tasks.",
  },
  {
    q: "How does progress tracking work?",
    a: "Progress signals are pulled from real sources like GitHub (commits, pull requests, code reviews). No self-reporting. The platform verifies actual work within 7-day collaboration cycles.",
  },
  {
    q: "Is Twig Loop free to use?",
    a: "The platform is currently in internal testing. During this phase, all core features are available at no cost. Pricing for production use will be announced before public launch.",
  },
  {
    q: "What can I do during Public Beta?",
    a: "Register an account, initiate projects (general, public-benefit, or recruitment), apply for open seats on existing projects, and view progress dashboards. All core collaboration features are operational.",
  },
  {
    q: "What is NOT available yet?",
    a: "GitHub source sync (automated progress signal ingestion), ClickHouse analytics dashboards, and Temporal durable workflows are not yet enabled. These features are planned for upcoming releases.",
  },
  {
    q: "How do I report issues?",
    a: "Report bugs and feature requests via GitHub Issues on the Twig Loop repository. Include steps to reproduce, expected behavior, and any error messages you encountered.",
  },
];

export default function HelpPage() {
  return (
    <div className="space-y-16 max-w-3xl">
      {/* Header */}
      <section>
        <h1 className="font-mono text-sm text-gray-500 mb-4">
          $ man twigloop
        </h1>
        <h2 className="font-mono text-2xl font-bold text-gray-100">
          Help Center
        </h2>
      </section>

      {/* What is Twig Loop */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## What is Twig Loop
        </h2>
        <div className="space-y-3 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            Twig Loop is an AI-native project collaboration platform. It helps
            people turn ideas and needs into structured, real collaboration.
          </p>
          <p>
            The platform uses MCP (Model Context Protocol) to interact with LLMs,
            structuring projects into work packages and task cards with clear
            goals, deliverables, and completion criteria.
          </p>
          <p>
            Progress is verified through real signals from external sources like
            GitHub, not self-reporting. The goal is to make collaboration
            trustworthy and efficient.
          </p>
        </div>
      </section>

      {/* Project Types */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Project Types
        </h2>
        <div className="space-y-4">
          <div className="border border-cyan-400/30 p-4">
            <h3 className="font-mono text-sm text-cyan-400 mb-2">
              General Projects
            </h3>
            <p className="font-mono text-xs text-gray-400 leading-relaxed">
              Standard project collaboration. A founder initiates the project,
              defines the scope, and the platform structures it. Collaborators
              apply for open seats and work on assigned task cards.
            </p>
          </div>
          <div className="border border-green-400/30 p-4">
            <h3 className="font-mono text-sm text-green-400 mb-2">
              Public Benefit Projects
            </h3>
            <p className="font-mono text-xs text-gray-400 leading-relaxed">
              Open-source or social-good projects. These require mandatory human
              review at key milestones. Reviewers verify quality and impact.
              Sponsors can provide financial support, resources, or mentorship
              through the SWU system.
            </p>
          </div>
          <div className="border border-yellow-400/30 p-4">
            <h3 className="font-mono text-sm text-yellow-400 mb-2">
              Recruitment Projects
            </h3>
            <p className="font-mono text-xs text-gray-400 leading-relaxed">
              Hiring-oriented projects. Instead of traditional interviews,
              candidates complete real task trials. Skills are verified through
              actual deliverables and code contributions (tracked via RWU).
            </p>
          </div>
        </div>
      </section>

      {/* Public Beta */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## Public Beta
        </h2>
        <div className="border border-green-400/30 p-4">
          <p className="font-mono text-xs text-green-400 mb-2">
            Public Beta
          </p>
          <div className="space-y-2 font-mono text-xs text-gray-400 leading-relaxed">
            <p>
              Twig Loop is now in Public Beta. Registration is open. Core
              features are operational: project initiation, work package
              structuring, collaborator matching, and task card management.
            </p>
            <p>
              During Public Beta, we are validating the main loop: initiate a
              project, structure it into tasks, match collaborators, and track
              real progress signals within 7-day collaboration cycles.
            </p>
            <p>
              Some advanced features (GitHub source sync, ClickHouse analytics,
              Temporal durable workflows) are not yet enabled and will be
              rolled out in upcoming releases.
            </p>
          </div>
        </div>
      </section>

      {/* MCP User Guide */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## MCP User Guide
        </h2>
        <div className="space-y-3 font-mono text-sm text-gray-400 leading-relaxed">
          <p>
            Twig Loop supports MCP Server (standard MCP protocol, JSON-RPC 2.0)
            for LLM-based interaction. MCP users can create and manage projects
            through their preferred AI assistant.
          </p>
          <div className="border border-gray-800 p-4 space-y-2">
            <p className="text-xs text-gray-500">
              <span className="text-gray-600">#</span> Connect via MCP Server
              (standard MCP protocol)
            </p>
            <p className="text-xs text-cyan-400">
              transport: stdio | sse
            </p>
            <p className="text-xs text-gray-500 mt-2">
              <span className="text-gray-600">#</span> Available operations
            </p>
            <p className="text-xs text-gray-400">
              - Create project (with AI structuring)
            </p>
            <p className="text-xs text-gray-400">
              - Browse and apply to projects
            </p>
            <p className="text-xs text-gray-400">
              - View task cards and work packages
            </p>
            <p className="text-xs text-gray-400">
              - Submit progress updates
            </p>
          </div>
          <p className="text-xs text-gray-500">
            Full MCP documentation will be available at public launch. Contact
            the team for early access.
          </p>
        </div>
      </section>

      {/* FAQ */}
      <section>
        <h2 className="font-mono text-sm text-green-400 mb-4">
          ## FAQ
        </h2>
        <div className="divide-y divide-gray-800">
          {FAQ_ITEMS.map((item, i) => (
            <div key={i} className="py-4">
              <h3 className="font-mono text-sm text-gray-100 mb-2">
                <span className="text-cyan-400 mr-2">Q:</span>
                {item.q}
              </h3>
              <p className="font-mono text-xs text-gray-400 leading-relaxed pl-6">
                {item.a}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Back to Home */}
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
