"use client";

import Link from "next/link";
import { useProjects } from "@/hooks/use-projects";

const STEPS = [
  { num: "01", title: "Project Enters", desc: "Initiator describes the project, the platform structures it into work packages and task cards." },
  { num: "02", title: "Work Structured", desc: "Each task has clear goals, deliverables, completion criteria, and estimated work units." },
  { num: "03", title: "Collaborators Connect", desc: "Contributors browse open seats, apply with their intended role, and get matched." },
  { num: "04", title: "Real Collaboration", desc: "Progress signals come from real sources (GitHub commits, PRs). No self-reporting." },
];

const PROJECT_TYPES = [
  {
    type: "General",
    color: "text-cyan-400",
    border: "border-cyan-400/30",
    desc: "Standard projects. Founder initiates, collaborators join, work gets done.",
  },
  {
    type: "Public Benefit",
    color: "text-green-400",
    border: "border-green-400/30",
    desc: "Open-source or social-good projects. Require human review at milestones. May receive sponsor support.",
  },
  {
    type: "Recruitment",
    color: "text-yellow-400",
    border: "border-yellow-400/30",
    desc: "Hiring-oriented. Real task trials replace traditional interviews. Skills verified through actual work.",
  },
];

export default function HomePage() {
  const { data: projRes } = useProjects();
  const projects = projRes?.data ?? [];
  const latestProjects = projects.slice(0, 3);

  const totalEwu = projects.reduce((sum, p) => sum + (p.total_ewu ?? 0), 0);
  const totalTasks = projects.reduce((sum, p) => sum + (p.task_count ?? 0), 0);
  const avgEwu =
    projects.length > 0
      ? (totalEwu / projects.length).toFixed(1)
      : "0";

  return (
    <div className="space-y-10">
      {/* Hero */}
      <section className="text-center py-6">
        <h1 className="font-mono text-6xl md:text-7xl font-bold text-green-400 tracking-tight">
          Twig Loop
        </h1>
        <p className="mt-4 font-mono text-lg text-gray-400 max-w-2xl mx-auto">
          MCP protocol. LLM interaction. Real collaboration.
        </p>
        <div className="mt-12 flex items-center justify-center gap-4">
          <Link
            href="/projects"
            className="font-mono px-6 py-2.5 bg-green-400/10 border border-green-400/40 text-green-400 hover:bg-green-400/20 transition-colors"
          >
            Browse Projects
          </Link>
          <Link
            href="/public-benefit/apply"
            className="font-mono px-6 py-2.5 bg-gray-800 border border-gray-700 text-gray-300 hover:bg-gray-700 transition-colors"
          >
            Public Benefit Request
          </Link>
        </div>
      </section>

      {/* Platform Intro */}
      <section className="max-w-3xl mx-auto">
        <h2 className="font-mono text-sm text-gray-500 mb-4">
          $ cat platform.txt
        </h2>
        <div className="space-y-3 font-mono text-sm">
          <p className="text-gray-400">
            <span className="text-red-400">NOT</span> a freelance marketplace.{" "}
            <span className="text-green-400">IS</span> a structured collaboration launcher.
          </p>
          <p className="text-gray-400">
            <span className="text-red-400">NOT</span> self-reported progress.{" "}
            <span className="text-green-400">IS</span> real signals from GitHub, code, and deliverables.
          </p>
          <p className="text-gray-400">
            <span className="text-red-400">NOT</span> AI replacing humans.{" "}
            <span className="text-green-400">IS</span> AI structuring work so humans collaborate better.
          </p>
          <p className="text-gray-400">
            <span className="text-red-400">NOT</span> another project management tool.{" "}
            <span className="text-green-400">IS</span> a protocol for turning ideas into verified teamwork.
          </p>
        </div>
      </section>

      {/* Recent Projects (live data) */}
      <section>
        <h2 className="font-mono text-sm text-gray-500 mb-6">
          $ curl /api/v1/projects?status=open
        </h2>
        {latestProjects.length > 0 ? (
          <>
            <p className="font-mono text-xs text-gray-600 mb-3">
              Showing latest 3 of {projects.length} projects
            </p>
            <div className="grid gap-3">
              {latestProjects.map((p) => (
                <Link
                  key={p.project_id}
                  href={`/projects/${p.project_id}`}
                  className="border border-gray-800 p-4 hover:border-green-400/30 transition-colors flex justify-between items-center"
                >
                  <div>
                    <span className="font-mono text-sm text-gray-200">
                      {p.title}
                    </span>
                    <span className="font-mono text-xs text-gray-600 ml-3">
                      {p.project_type}
                    </span>
                  </div>
                  <span className="text-xs font-mono text-gray-500">
                    {p.status}
                  </span>
                </Link>
              ))}
            </div>
          </>
        ) : (
          <div className="border border-gray-800 p-8 text-center">
            <p className="font-mono text-sm text-gray-600">
              No projects yet
            </p>
          </div>
        )}
      </section>

      {/* Platform Status (live data) */}
      <section>
        <h2 className="font-mono text-sm text-gray-500 mb-6">
          $ status --summary
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatusMetric label="Projects" value={projects.length} />
          <StatusMetric label="Tasks" value={totalTasks} />
          <StatusMetric label="Total EWU" value={totalEwu} />
          <StatusMetric label="Avg EWU" value={avgEwu} />
        </div>
      </section>

      {/* How It Works */}
      <section>
        <h2 className="font-mono text-sm text-gray-500 mb-6">
          $ ./how-it-works --steps
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {STEPS.map((step) => (
            <div
              key={step.num}
              className="border border-gray-800 p-5 hover:border-green-400/30 transition-colors"
            >
              <div className="font-mono text-green-400 text-xs mb-2">
                [{step.num}]
              </div>
              <h3 className="font-mono text-sm font-semibold text-gray-100 mb-2">
                {step.title}
              </h3>
              <p className="text-xs text-gray-500 leading-relaxed">
                {step.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Project Types */}
      <section>
        <h2 className="font-mono text-sm text-gray-500 mb-6">
          $ ls project-types/
        </h2>
        <div className="grid md:grid-cols-3 gap-4">
          {PROJECT_TYPES.map((pt) => (
            <div
              key={pt.type}
              className={`border ${pt.border} p-5`}
            >
              <h3 className={`font-mono text-sm font-semibold ${pt.color} mb-2`}>
                {pt.type}
              </h3>
              <p className="text-xs text-gray-500 leading-relaxed">
                {pt.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Get Started */}
      <section>
        <h2 className="font-mono text-sm text-gray-500 mb-6">
          $ ./start --help
        </h2>
        <div className="grid md:grid-cols-2 gap-4">
          <Link
            href="/projects"
            className="border border-gray-800 p-5 hover:border-green-400/30 transition-colors group"
          >
            <h3 className="font-mono text-sm font-semibold text-gray-100 mb-2 group-hover:text-green-400 transition-colors">
              Use Platform
            </h3>
            <p className="text-xs text-gray-500 leading-relaxed mb-4">
              Browse projects, apply to open seats, or initiate your own project.
            </p>
            <span className="font-mono text-xs text-cyan-400">
              {">"} Browse Projects
            </span>
          </Link>
          <div className="border border-gray-800 p-5">
            <h3 className="font-mono text-sm font-semibold text-gray-100 mb-2">
              Run Locally
            </h3>
            <p className="text-xs text-gray-500 leading-relaxed mb-4">
              Clone the repo, start the dev server, and explore.
            </p>
            <code className="font-mono text-xs text-cyan-400 block break-all">
              git clone https://github.com/TwigLoop/TwigLoopOpen.git
            </code>
          </div>
        </div>
      </section>
    </div>
  );
}

function StatusMetric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="border border-gray-800 p-4 text-center">
      <div className="font-mono text-2xl text-green-400 font-bold">
        {value}
      </div>
      <div className="font-mono text-xs text-gray-500 mt-1">
        {label}
      </div>
    </div>
  );
}
