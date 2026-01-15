"use client";

import "./globals.css";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { useState } from "react";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navItems = [
    { name: "Memory Overview", href: "/memory", icon: "psychology" },
    { name: "Connected Apps", href: "/connected", icon: "hub" },
    { name: "Query Assistant", href: "/query", icon: "chat_bubble" },

    { name: "Live Tracking", href: "/live-tracking", icon: "sensors" },
  ];

  const NavContent = () => (
    <div>
      <Link href="/" className="flex items-center gap-3 px-2">
        <div className="w-32 h-16 flex items-center justify-center">
          <img src="/logo.svg" alt="Backboard Logo" className="w-full h-full object-contain" />
        </div>

      </Link>


      <nav className="flex flex-col gap-1.5 mt-8">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setIsMobileMenuOpen(false)}
              className={`nav-link ${isActive ? "nav-link-active" : ""}`}
            >
              <span className="material-symbols-outlined opacity-80">{item.icon}</span>
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto pt-6 border-t border-zinc-800/50">
        <Link href="/profile" className="px-2 py-3 bg-zinc-800/30 rounded-full border border-zinc-700/30 flex items-center gap-3 hover:bg-zinc-800/50 transition-colors group">
          <div className="w-10 h-10 rounded-full bg-zinc-700/50 flex items-center justify-center text-zinc-400 group-hover:text-white transition-colors">
            <span className="material-symbols-outlined text-2xl">account_circle</span>
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-semibold group-hover:text-indigo-400 transition-colors">User</span>
            <span className="text-[10px] text-zinc-500 uppercase tracking-wider">Free Plan</span>
          </div>
        </Link>
      </div>
    </div>
  );

  const isAuthPage = pathname === '/signin' || pathname === '/signup';

  if (isAuthPage) {
    return (
      <html lang="en" className="dark">
        <head>
          <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
        </head>
        <body className="antialiased">
          {children}
        </body>
      </html>
    );
  }

  return (
    <html lang="en" className="dark">
      <head>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
      </head>
      <body className="antialiased">
        <div className="relative min-h-screen flex text-zinc-100">
          {/* Background decoration */}
          <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
            <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-indigo-500/10 blur-[120px] rounded-full" />
            <div className="absolute top-[20%] -right-[10%] w-[35%] h-[35%] bg-purple-500/10 blur-[120px] rounded-full" />
            <div className="absolute bottom-[-10%] left-[0%] w-[30%] h-[30%] bg-blue-500/10 blur-[120px] rounded-full" />
          </div>

          {/* Desktop Sidebar */}
          <aside className="sticky top-0 h-screen w-72 glass-card border-l-0 border-y-0 p-6 flex flex-col hidden md:flex shrink-0 overflow-y-auto">
            <NavContent />
          </aside>

          {/* Mobile Sidebar Overlay */}
          {isMobileMenuOpen && (
            <div
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden"
              onClick={() => setIsMobileMenuOpen(false)}
            />
          )}

          {/* Mobile Sidebar */}
          <aside className={`fixed top-0 left-0 bottom-0 w-72 glass-card border-l-0 border-y-0 p-6 flex flex-col z-50 transition-transform duration-300 md:hidden ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}`}>
            <NavContent />
          </aside>

          {/* Main Content */}
          <main className="flex-1 overflow-auto bg-zinc-950/20">
            <header className="h-16 border-b border-zinc-800/50 flex items-center justify-between px-6 bg-zinc-950/40 backdrop-blur-sm sticky top-0 z-10 md:hidden">
              <div className="flex items-center gap-3 text-white">
                <button
                  onClick={() => setIsMobileMenuOpen(true)}
                  className="p-2 -ml-2 hover:bg-zinc-800/50 rounded-full transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
                  </svg>
                </button>
                <Link href="/" className="flex items-center justify-center w-32 h-14">
                  <img src="/logo.svg" alt="Backboard Logo" className="w-full h-full object-contain" />
                </Link>
              </div>
            </header>
            <div className="p-6 md:p-8 max-w-7xl mx-auto">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}
