"use client";

import "./globals.css";
import Link from "next/link";
import { useEffect } from "react";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  useEffect(() => {
    const buttons = document.querySelectorAll(".ripple");
    buttons.forEach((button) => {
      button.addEventListener("click", (event) => {
        event.preventDefault();
        const div = document.createElement("div");
        const rect = button.getBoundingClientRect();
        const xPos = (event as MouseEvent).clientX - rect.left;
        const yPos = (event as MouseEvent).clientY - rect.top;
        div.classList.add("ripple-effect");
        const size = (button as HTMLElement).offsetHeight;
        div.style.height = size + "px";
        div.style.width = size + "px";
        div.style.top = yPos - size / 2 + "px";
        div.style.left = xPos - size / 2 + "px";
        div.style.background =
          (button as HTMLElement).dataset.rippleColor || "white";
        button.appendChild(div);
        setTimeout(() => {
          div.remove();
        }, 2000);
      });
    });
  }, []);

  return (
    <html lang="en">
      <body>
        <div className="min-h-screen flex">
          <aside className="w-72 bg-white border-r p-4">
            <h1 className="text-xl font-semibold mb-4">Backboard</h1>
            <nav className="flex flex-col gap-2">
              <Link
                className="px-3 py-2 rounded hover:bg-gray-100"
                href="/memory"
              >
                Memory Overview
              </Link>
              <Link
                className="px-3 py-2 rounded hover:bg-gray-100"
                href="/connected"
              >
                Connected Apps
              </Link>
              <Link
                className="px-3 py-2 rounded hover:bg-gray-100"
                href="/query"
              >
                Query
              </Link>
              <Link
                className="px-3 py-2 rounded hover:bg-gray-100"
                href="/settings"
              >
                API Settings
              </Link>
              <Link
                className="px-3 py-2 rounded hover:bg-gray-100"
                href="/live-tracking"
              >
                Live Tracking
              </Link>
            </nav>
          </aside>

          <main className="flex-1 p-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
