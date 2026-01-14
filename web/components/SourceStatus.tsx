import React from "react";

type Props = {
  drive?: { connected: boolean; lastUpdated?: string };
  codebase?: { connected: boolean; lastUpdated?: string };
  telegram?: { connected: boolean; lastUpdated?: string };
  summarizer?: {
    status: "idle" | "running" | "failed" | "ok";
    lastRun?: string;
  };
};

export default function SourceStatus({
  drive,
  codebase,
  telegram,
  summarizer,
}: Props) {
  const sources = [
    { name: "Google Drive", data: drive, icon: "add_to_drive" },
    { name: "Codebase", data: codebase, icon: "terminal" },
    { name: "Telegram Bot", data: telegram, icon: "send" },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in duration-500">
      <div className="glass-card p-6 rounded-3xl">
        <div className="flex items-center gap-3 mb-6">
          <div className="material-symbols-outlined text-zinc-400">tune</div>
          <h3 className="text-lg font-bold">Data Sources</h3>
        </div>
        <div className="space-y-4">
          {sources.map((source) => (
            <div key={source.name} className="flex justify-between items-center p-4 bg-zinc-900/50 rounded-2xl border border-zinc-800/50">
              <div className="flex items-center gap-4">
                <div className="material-symbols-outlined text-2xl opacity-80 text-zinc-400">{source.icon}</div>
                <div>
                  <div className="font-semibold">{source.name}</div>
                  <div className="text-xs text-zinc-500">
                    Sync: {source.data?.lastUpdated ?? "Never"}
                  </div>
                </div>
              </div>
              <div
                className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${source.data?.connected
                  ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
                  : "bg-red-500/10 text-red-500 border border-red-500/20"
                  }`}
              >
                {source.data?.connected ? "Online" : "Offline"}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="glass-card p-6 rounded-3xl">
        <div className="flex items-center gap-3 mb-6">
          <div className="material-symbols-outlined text-zinc-400">smart_toy</div>
          <h3 className="text-lg font-bold">Intelligence Engine</h3>
        </div>
        <div className="space-y-6">
          <div className="p-4 bg-zinc-900/50 rounded-2xl border border-zinc-800/50">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-zinc-400">Memory Sync Status</span>
              <span
                className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${summarizer?.status === "running"
                  ? "bg-amber-500/10 text-amber-500 border border-amber-500/20"
                  : summarizer?.status === "ok"
                    ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
                    : "bg-red-500/10 text-red-500 border border-red-500/20"
                  }`}
              >
                {summarizer?.status || "Idle"}
              </span>
            </div>
            <div className="text-sm font-bold">{summarizer?.lastRun || "No activity recorded"}</div>
          </div>

          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-widest text-zinc-500">Processing Insights</h4>
            <p className="text-sm text-zinc-400 leading-relaxed">
              The extraction pipeline is monitoring connected nodes for updates.
              New fragments are automatically vector-indexed into your Backboard LLM Memory.
            </p>
            <div className="pt-2">
              <button className="btn-secondary w-full py-2.5 text-sm">
                Manually Request Sync
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
