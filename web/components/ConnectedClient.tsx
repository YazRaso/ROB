"use client";

import { useState, useEffect } from "react";
import DemoToggle from "./DemoToggle";
import SourceStatus from "./SourceStatus";
import { API } from "../lib/api";

export default function ConnectedClient() {
  const [demoEnabled, setDemoEnabled] = useState(true);
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    if (!demoEnabled) {
      API.getStatus().then(setStatus).catch(console.error);
    }
  }, [demoEnabled]);

  const drive = demoEnabled
    ? { connected: true, lastUpdated: "2026-01-12 12:20 UTC" }
    : { connected: status?.drive?.connected, lastUpdated: status?.drive?.lastUpdated };

  const codebase = demoEnabled
    ? { connected: true, lastUpdated: "2026-01-12 12:20 UTC" }
    : { connected: status?.codebase?.connected, lastUpdated: status?.codebase?.lastUpdated };

  const telegram = demoEnabled
    ? { connected: false }
    : { connected: status?.telegram?.connected, lastUpdated: status?.telegram?.lastUpdated };

  const summarizer = {
    status: (demoEnabled ? "ok" : (status?.client?.exists ? "ok" : "idle")) as "ok" | "idle",
    lastRun: demoEnabled ? "2026-01-12 12:20 UTC" : status?.drive?.lastUpdated,
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header className="space-y-2">
        <h2 className="text-3xl font-extrabold tracking-tight text-white">Integration Hub</h2>
        <p className="text-zinc-400">
          Manage your external data connectors and configure automated ingestion protocols.
        </p>
      </header>

      <DemoToggle
        enabled={demoEnabled}
        onToggle={() => setDemoEnabled(!demoEnabled)}
      />

      <SourceStatus
        drive={drive}
        codebase={codebase}
        telegram={telegram}
        summarizer={summarizer}
      />

      <div className="glass-card p-8 rounded-3xl border-zinc-800/30">
        <div className="flex items-center gap-3 mb-4">
          <div className="material-symbols-outlined text-zinc-400">build</div>
          <h3 className="text-lg font-bold">Manual Connectors</h3>
        </div>
        <p className="text-sm text-zinc-500 leading-relaxed max-w-2xl">
          In a production environment, these nodes are bridged via industrial-standard OAuth2.0 flows and real-time webhook subscribers
          to continuously stream delta updates into the Backboard memory system.
        </p>
        <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-4">
          <button className="btn-secondary py-3 text-sm">Configure Webhooks</button>
          <button className="btn-secondary py-3 text-sm">View API Documentation</button>
        </div>
      </div>
    </div>
  );
}
