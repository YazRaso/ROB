"use client";

import { useState, useEffect } from "react";
import SourceStatus from "../../components/SourceStatus";
import { API } from "../../lib/api";

export default function MemoryPage() {
  const [status, setStatus] = useState<any>(null);
  const [activity, setActivity] = useState<any[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statusData, activityData] = await Promise.all([
          API.getStatus(),
          API.getActivity()
        ]);
        setStatus(statusData);
        setActivity(activityData);
      } catch (err) {
        console.error(err);
      }
    };

    fetchData();
  }, []);

  const drive = {
    connected: status?.drive?.connected ?? false,
    lastUpdated: status?.drive?.lastUpdated ?? "Never"
  };
  const codebase = {
    connected: status?.codebase?.connected ?? true,
    lastUpdated: status?.codebase?.lastUpdated ?? "2026-01-12 09:55 UTC"
  };
  const telegram = {
    connected: status?.telegram?.connected ?? false
  };
  const summarizer = {
    status: (status?.client?.exists ? "ok" : "idle") as any,
    lastRun: status?.drive?.lastUpdated ?? "Never"
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header className="space-y-2">
        <h2 className="text-3xl font-extrabold tracking-tight text-white">Memory Overview</h2>
        <p className="text-zinc-400">
          Real-time status of connected intelligence nodes and synchronization frequency.
        </p>
      </header>

      <SourceStatus
        drive={drive}
        codebase={codebase}
        telegram={telegram}
        summarizer={summarizer}
      />

      <div className="glass-card p-8 rounded-3xl">
        <div className="flex items-center gap-3 mb-6">
          <div className="material-symbols-outlined text-zinc-400">history</div>
          <h3 className="text-lg font-bold">Activity Log</h3>
        </div>
        <div className="space-y-4">
          {activity.length === 0 ? (
            <div className="text-center py-12 text-zinc-500 italic">
              No recent activity recorded.
            </div>
          ) : (
            activity.map((item, i) => {
              const iconMap = {
                Drive: "add_to_drive",
                GitHub: "terminal",
                Telegram: "send"
              };
              const iconName = iconMap[item.source as keyof typeof iconMap] || "info";

              return (
                <div key={i} className="flex items-start gap-4 p-4 bg-zinc-900/40 rounded-2xl border border-zinc-800/50 transition-colors hover:bg-zinc-800/40">
                  <div className={`w-10 h-10 rounded-xl bg-${item.color}-500/10 flex items-center justify-center text-${item.color}-500`}>
                    <span className="material-symbols-outlined text-xl">{iconName}</span>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{item.title}</p>
                    <p className="text-xs text-zinc-500 mt-1">{item.time} • {item.summary}</p>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
