import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Platform Status | Twig Loop",
  description: "Twig Loop platform status and metrics dashboard",
};

const CORE_METRICS = [
  { label: "Total Public Projects", value: "--", change: null },
  { label: "Open Projects", value: "--", change: null },
  { label: "Active Tasks", value: "--", change: null },
  { label: "Open Seats", value: "--", change: null },
  { label: "Public Benefit Requests", value: "--", change: null },
  { label: "MCP Users", value: "--", change: null },
];

const RECENT_CHANGES = [
  { date: "---", event: "Awaiting live data from core-api" },
];

const SYSTEM_NOTES = [
  "Platform is in internal testing phase (MVP baseline complete)",
  "22 specs implemented, all core workflows operational",
  "Source sync via GitHub webhooks is active",
  "ClickHouse analytics pipeline ready",
  "Public registration not yet open",
];

export default function StatusPage() {
  const statusLevel = "Internal Testing";
  const statusColor = "text-yellow-400";
  const statusBorder = "border-yellow-400/40";
  const statusBg = "bg-yellow-400/10";

  return (
    <div className="space-y-12">
      {/* Header */}
      <section>
        <h1 className="font-mono text-sm text-gray-500 mb-4">
          $ status --verbose
        </h1>
        <div className="flex items-center gap-4">
          <h2 className="font-mono text-2xl font-bold text-gray-100">
            Platform Status
          </h2>
          <span
            className={`font-mono text-xs px-3 py-1 border ${statusBorder} ${statusBg} ${statusColor}`}
          >
            {statusLevel}
          </span>
        </div>
      </section>

      {/* Core Metrics */}
      <section>
        <h2 className="font-mono text-sm text-gray-500 mb-4">
          $ metrics --core
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {CORE_METRICS.map((m) => (
            <div
              key={m.label}
              className="border border-gray-800 p-5"
            >
              <div className="font-mono text-3xl text-green-400 font-bold">
                {m.value}
              </div>
              <div className="font-mono text-xs text-gray-500 mt-2">
                {m.label}
              </div>
              {m.change != null && (
                <div className="font-mono text-xs text-cyan-400 mt-1">
                  +{m.change} this week
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Last 7 Days */}
      <section>
        <h2 className="font-mono text-sm text-gray-500 mb-4">
          $ log --since=7d
        </h2>
        <div className="border border-gray-800 divide-y divide-gray-800">
          {RECENT_CHANGES.map((item, i) => (
            <div key={i} className="flex items-start gap-4 p-4">
              <span className="font-mono text-xs text-gray-600 shrink-0 w-24">
                {item.date}
              </span>
              <span className="font-mono text-xs text-gray-400">
                {item.event}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* System Notes */}
      <section>
        <h2 className="font-mono text-sm text-gray-500 mb-4">
          $ cat /etc/twigloop/notes
        </h2>
        <div className="border border-gray-800 p-5 space-y-2">
          {SYSTEM_NOTES.map((note, i) => (
            <p key={i} className="font-mono text-xs text-gray-400">
              <span className="text-gray-600 mr-2">#</span>
              {note}
            </p>
          ))}
        </div>
      </section>
    </div>
  );
}
