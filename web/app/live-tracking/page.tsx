"use client";

import { useState, useEffect } from "react";
import Script from "next/script";
import { API } from "../../lib/api";

export default function LiveTrackingPage() {
  const [updates, setUpdates] = useState<any[]>([]);

  const formatTime = (timeStr: string) => {
    try {
      // Handle SQLite format YYYY-MM-DD HH:MM:SS
      const date = new Date(timeStr.replace(' ', 'T'));
      if (isNaN(date.getTime())) return timeStr;
      return date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
    } catch (e) {
      return timeStr;
    }
  };

  useEffect(() => {
    const fetchActivity = async () => {
      try {
        const data = await API.getActivity();
        if (data.length > 0) {
          setUpdates(data);
        } else {
          // Fallback to mock data for demo if DB is empty
          setUpdates([
            // Google Drive entries
            { source: "Drive", title: "Document 'Q4 Product Roadmap' synced", summary: "Indexed 45 pages with key milestones and deliverables", time: "3:45 PM", color: "emerald" },
            { source: "Drive", title: "Spreadsheet 'Budget 2024' updated", summary: "Detected 8 new formulas and 3 pivot tables", time: "2:30 PM", color: "emerald" },
            { source: "Drive", title: "Presentation 'Team Standup' analyzed", summary: "Extracted action items from 12 slides", time: "1:15 PM", color: "emerald" },
            // Codebase/Repo entries
            { source: "GitHub", title: "New commit pushed to branch 'main'", summary: "Refactored UI components for global consistency", time: "3:20 PM", color: "blue" },
            { source: "GitHub", title: "Pull request #142 merged", summary: "Added SSE support for real-time notifications", time: "2:45 PM", color: "blue" },
            { source: "GitHub", title: "Branch 'feature/auth' created", summary: "Started implementation of OAuth2 flow", time: "11:30 AM", color: "blue" },
            // Telegram entries
            { source: "Telegram", title: "Message batch from #dev-ops", summary: "Processed 23 messages about deployment pipeline", time: "3:10 PM", color: "purple" },
            { source: "Telegram", title: "New thread in #general", summary: "Extracted context from team discussion on architecture", time: "2:00 PM", color: "purple" },
            { source: "Telegram", title: "File shared in #resources", summary: "Indexed PDF document 'API Documentation v2'", time: "12:45 PM", color: "purple" },
          ]);
        }
      } catch (err) {
        console.error(err);
        // Fallback to mock data when backend is unavailable
        setUpdates([
          // Google Drive entries
          { source: "Drive", title: "Document 'Q4 Product Roadmap' synced", summary: "Indexed 45 pages with key milestones and deliverables", time: "3:45 PM", color: "emerald" },
          { source: "Drive", title: "Spreadsheet 'Budget 2024' updated", summary: "Detected 8 new formulas and 3 pivot tables", time: "2:30 PM", color: "emerald" },
          { source: "Drive", title: "Presentation 'Team Standup' analyzed", summary: "Extracted action items from 12 slides", time: "1:15 PM", color: "emerald" },
          // Codebase/Repo entries
          { source: "GitHub", title: "New commit pushed to branch 'main'", summary: "Refactored UI components for global consistency", time: "3:20 PM", color: "blue" },
          { source: "GitHub", title: "Pull request #142 merged", summary: "Added SSE support for real-time notifications", time: "2:45 PM", color: "blue" },
          { source: "GitHub", title: "Branch 'feature/auth' created", summary: "Started implementation of OAuth2 flow", time: "11:30 AM", color: "blue" },
          // Telegram entries
          { source: "Telegram", title: "Message batch from #dev-ops", summary: "Processed 23 messages about deployment pipeline", time: "3:10 PM", color: "purple" },
          { source: "Telegram", title: "New thread in #general", summary: "Extracted context from team discussion on architecture", time: "2:00 PM", color: "purple" },
          { source: "Telegram", title: "File shared in #resources", summary: "Indexed PDF document 'API Documentation v2'", time: "12:45 PM", color: "purple" },
        ]);
      }
    };


    fetchActivity();

    // Subscribe to SSE for real-time updates
    const unsubscribe = API.subscribeToEvents((event) => {
      console.log("Received event:", event);
      // Refresh activity when we receive an event
      fetchActivity();
    });

    return () => unsubscribe();
  }, []);

  useEffect(() => {
    // Check if the script is already loaded
    if (typeof window !== "undefined" && (window as any).Globe) {
      initializeGlobe();
    }
  }, []);

  const initializeGlobe = () => {
    // Gen random data with modern colors
    const N = 24;
    const colors = ["#6366f1", "#a855f7", "#ec4899", "#3b82f6", "#10b981"];
    const arcsData = Array.from({ length: N }, () => ({
      startLat: (Math.random() - 0.5) * 180,
      startLng: (Math.random() - 0.5) * 360,
      endLat: (Math.random() - 0.5) * 180,
      endLng: (Math.random() - 0.5) * 360,
      color: [
        colors[Math.floor(Math.random() * colors.length)],
        colors[Math.floor(Math.random() * colors.length)],
      ],
    }));

    if (typeof window !== "undefined" && (window as any).Globe) {
      const globeElement = document.getElementById("globeViz");
      if (globeElement) {
        // Clear previous instance if any
        globeElement.innerHTML = '';

        // Explicitly set dimensions to match container
        const width = globeElement.clientWidth;
        const height = globeElement.clientHeight;

        new (window as any).Globe(globeElement)
          .width(width)
          .height(height)
          .globeImageUrl(
            "//cdn.jsdelivr.net/npm/three-globe/example/img/earth-night.jpg"
          )
          .backgroundColor("rgba(0,0,0,0)")
          .arcsData(arcsData)
          .arcColor("color")
          .arcDashLength(() => 0.4)
          .arcDashGap(() => 0.1)
          .arcDashAnimateTime(() => Math.random() * 3000 + 1000)
          .arcStroke(0.5)
          .atmosphereColor("#6366f1")
          .atmosphereAltitude(0.15);
      }
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <Script src="//cdn.jsdelivr.net/npm/globe.gl" onLoad={initializeGlobe} />

      <header className="space-y-2">
        <h2 className="text-3xl font-extrabold tracking-tight text-white">Live Operations</h2>
        <p className="text-zinc-400">
          Real-time visualization of data ingestion and intelligence mapping across global nodes.
        </p>
      </header>

      <div className="flex flex-col gap-8">
        {/* Full width globe centered */}
        <div className="relative glass-card rounded-3xl overflow-hidden h-[600px] flex items-center justify-center w-full shadow-2xl shadow-indigo-500/10">
          <div className="absolute inset-0 bg-gradient-to-b from-indigo-500/5 to-transparent pointer-events-none" />
          <div id="globeViz" className="w-full h-full cursor-grab active:cursor-grabbing"></div>
          <div className="absolute bottom-6 left-6 flex items-center gap-2 px-3 py-1.5 bg-black/40 backdrop-blur-md rounded-lg border border-zinc-800/50">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[10px] uppercase font-bold tracking-widest text-zinc-300">Live Telemetry Active</span>
          </div>
        </div>

        <div className="flex flex-col gap-8">
          {/* Google Drive Section */}
          <div className="glass-card p-6 rounded-3xl border-zinc-800/30">
            <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
              <span className="material-symbols-outlined text-emerald-500">add_to_drive</span>
              Google Drive
            </h3>
            <div className="space-y-4">
              {updates.filter(u => u.source === "Drive").map((update, i) => (
                <div key={i} className="group relative p-4 rounded-2xl bg-zinc-900/50 border border-zinc-800/50 hover:border-emerald-500/50 transition-all hover:bg-zinc-800/50">
                  <div className="flex items-start gap-4">
                    <div className="w-2 h-2 mt-1.5 rounded-full bg-emerald-500 shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="ml-auto text-[10px] font-medium text-zinc-500">{formatTime(update.time)}</span>
                      </div>
                      <p className="text-sm font-medium text-zinc-200 truncate">{update.title}</p>
                      <p className="text-xs text-zinc-500 line-clamp-2 mt-1">{update.summary}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* GitHub Section */}
          <div className="glass-card p-6 rounded-3xl border-zinc-800/30">
            <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
              <span className="material-symbols-outlined text-blue-500">terminal</span>
              GitHub
            </h3>
            <div className="space-y-4">
              {updates.filter(u => u.source === "GitHub").map((update, i) => (
                <div key={i} className="group relative p-4 rounded-2xl bg-zinc-900/50 border border-zinc-800/50 hover:border-blue-500/50 transition-all hover:bg-zinc-800/50">
                  <div className="flex items-start gap-4">
                    <div className="w-2 h-2 mt-1.5 rounded-full bg-blue-500 shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="ml-auto text-[10px] font-medium text-zinc-500">{formatTime(update.time)}</span>
                      </div>
                      <p className="text-sm font-medium text-zinc-200 truncate">{update.title}</p>
                      <p className="text-xs text-zinc-500 line-clamp-2 mt-1">{update.summary}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Telegram Section */}
          <div className="glass-card p-6 rounded-3xl border-zinc-800/30">
            <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
              <span className="material-symbols-outlined text-purple-500">send</span>
              Telegram
            </h3>
            <div className="space-y-4">
              {updates.filter(u => u.source === "Telegram").map((update, i) => (
                <div key={i} className="group relative p-4 rounded-2xl bg-zinc-900/50 border border-zinc-800/50 hover:border-purple-500/50 transition-all hover:bg-zinc-800/50">
                  <div className="flex items-start gap-4">
                    <div className="w-2 h-2 mt-1.5 rounded-full bg-purple-500 shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="ml-auto text-[10px] font-medium text-zinc-500">{formatTime(update.time)}</span>
                      </div>
                      <p className="text-sm font-medium text-zinc-200 truncate">{update.title}</p>
                      <p className="text-xs text-zinc-500 line-clamp-2 mt-1">{update.summary}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="flex justify-center">
          <button className="btn-secondary py-2 px-6 text-xs uppercase tracking-widest font-bold opacity-70 hover:opacity-100 transition-opacity">
            View Full Logs
          </button>
        </div>
      </div>
    </div>
  );
}
