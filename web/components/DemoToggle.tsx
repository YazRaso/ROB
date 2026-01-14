import React from "react";

export default function DemoToggle({
  enabled,
  onToggle,
}: {
  enabled: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="p-6 glass-card rounded-3xl flex items-center justify-between gap-6 border-zinc-800/30 group">
      <div className="flex items-center gap-4">
        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center text-2xl transition-all duration-300 ${enabled ? "bg-indigo-500/10 text-indigo-400 rotate-0" : "bg-zinc-800 text-zinc-500 -rotate-12 group-hover:rotate-0"}`}>
          <span className="material-symbols-outlined">rocket_launch</span>
        </div>
        <div>
          <div className="font-bold text-white">Simulation Engine</div>
          <div className="text-xs text-zinc-500 mt-1 max-w-sm">
            Toggle the hardcoded demo environment to simulate live integrations and guided context extraction without active API calls.
          </div>
        </div>
      </div>
      <div>
        <button
          onClick={onToggle}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-zinc-900 ${enabled ? "bg-indigo-600" : "bg-zinc-700"
            }`}
        >
          <span
            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${enabled ? "translate-x-6" : "translate-x-1"
              }`}
          />
        </button>
      </div>
    </div>
  );
}
