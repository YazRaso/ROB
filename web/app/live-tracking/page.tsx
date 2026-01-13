"use client";

import React from "react";
import Script from "next/script";

export default function LiveTrackingPage() {
  const initializeGlobe = () => {
    // Gen random data
    const N = 20;
    const arcsData = Array.from({ length: N }, () => ({
      startLat: (Math.random() - 0.5) * 180,
      startLng: (Math.random() - 0.5) * 360,
      endLat: (Math.random() - 0.5) * 180,
      endLng: (Math.random() - 0.5) * 360,
      color: [
        ["red", "white", "blue", "green"][Math.round(Math.random() * 3)],
        ["red", "white", "blue", "green"][Math.round(Math.random() * 3)],
      ],
    }));

    if (typeof window !== "undefined" && (window as any).Globe) {
      new (window as any).Globe(document.getElementById("globeViz"))
        .globeImageUrl(
          "//cdn.jsdelivr.net/npm/three-globe/example/img/earth-night.jpg"
        )
        .arcsData(arcsData)
        .arcColor("color")
        .arcDashLength(() => Math.random())
        .arcDashGap(() => Math.random())
        .arcDashAnimateTime(() => Math.random() * 4000 + 500);
    }
  };

  return (
    <div className="space-y-4">
      <Script src="//cdn.jsdelivr.net/npm/globe.gl" onLoad={initializeGlobe} />
      <h1 className="text-3xl font-bold">Live Tracking</h1>
      <p className="text-gray-600">
        Real-time updates on new context uploaded from connected sources.
      </p>

      <div className="space-y-4">
        {/* Placeholder for live updates */}
        <div className="bg-white p-4 rounded shadow">
          <h3 className="font-medium">Recent Updates</h3>
          <div className="mt-2 space-y-2">
            {/* Example update */}
            <div className="border-l-4 border-blue-500 pl-4">
              <p className="text-sm text-gray-600">Source: GitHub</p>
              <p className="text-sm">New commit pushed to main branch</p>
              <p className="text-xs text-gray-500">
                Summary: Updated README with installation instructions
              </p>
              <p className="text-xs text-gray-500">
                Timestamp: 2026-01-12 12:20 UTC
              </p>
            </div>
            <div className="border-l-4 border-green-500 pl-4">
              <p className="text-sm text-gray-600">Source: Drive</p>
              <p className="text-sm">New document uploaded</p>
              <p className="text-xs text-gray-500">
                Summary: Project proposal document added
              </p>
              <p className="text-xs text-gray-500">
                Timestamp: 2026-01-12 12:15 UTC
              </p>
            </div>
            <div className="border-l-4 border-purple-500 pl-4">
              <p className="text-sm text-gray-600">Source: Telegram</p>
              <p className="text-sm">New message in channel</p>
              <p className="text-xs text-gray-500">
                Summary: Team discussion on feature implementation
              </p>
              <p className="text-xs text-gray-500">
                Timestamp: 2026-01-12 12:10 UTC
              </p>
            </div>
          </div>
        </div>
      </div>

      <div id="globeViz" style={{ width: "100%", height: "600px" }}></div>
    </div>
  );
}
