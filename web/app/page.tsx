import Link from "next/link";

export default function Home() {
  const hasKey = !!process.env.BACKBOARD_API_KEY;

  const cards = [
    {
      title: "Memory Overview",
      description: "Visualize connected data sources and historical activity logs in real-time.",
      href: "/memory",
      icon: "psychology",
      color: "from-blue-500/20 to-indigo-500/20",
    },
    {
      title: "Connected Apps",
      description: "Integrate with Google Drive, Telegram, and Jira to enrich your AI context.",
      href: "/connected",
      icon: "hub",
      color: "from-purple-500/20 to-pink-500/20",
    },
    {
      title: "Query Assistant",
      description: "Interact with your collected knowledge using our specialized chat interface.",
      href: "/query",
      icon: "forum",
      color: "from-emerald-500/20 to-teal-500/20",
    },
    {
      title: "API Settings",
      description: "Manage your authentication keys and global configuration parameters.",
      href: "/settings",
      icon: "settings_suggest",
      color: "from-orange-500/20 to-amber-500/20",
    },
  ];

  return (
    <div className="space-y-10 py-4 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header className="space-y-4">
        <div className="inline-flex items-center px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-xs font-medium text-indigo-400">
          Welcome back to Backboard
        </div>
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-zinc-200 to-zinc-500">
          Command Center
        </h1>
        <p className="text-zinc-400 text-lg max-w-2xl leading-relaxed">
          The ultimate interface for managing your team's distributed knowledge.
          Bridge the gap between informal chats and formal documentation.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {cards.map((card) => (
          <Link
            key={card.href}
            href={card.href}
            className="
        group relative overflow-hidden
        p-8 rounded-3xl
        border border-zinc-800
        bg-zinc-900/60
        transition-all duration-300
        hover:scale-[1.02]
        hover:border-blue-500/40
        hover:bg-blue-950/40
      "
          >
            <div className="relative z-10">
              <div
                className="
            w-14 h-14 rounded-2xl
            bg-zinc-900
            border border-zinc-800
            flex items-center justify-center
            text-3xl mb-6
            shadow-xl
            group-hover:scale-110
            transition-transform duration-300
          "
              >
                <span className="material-symbols-outlined text-4xl text-blue-400">
                  {card.icon}
                </span>
              </div>

              <h3
                className="
            text-2xl font-bold mb-3
            text-zinc-100
            group-hover:text-blue-400
            transition-colors
          "
              >
                {card.title}
              </h3>

              <p
                className="
            text-zinc-400 leading-relaxed
            group-hover:text-zinc-300
            transition-colors
          "
              >
                {card.description}
              </p>

              <div
                className="
            mt-6 flex items-center
            text-xs font-semibold uppercase tracking-widest
            text-blue-500
            opacity-0
            transform -translate-x-2
            group-hover:opacity-100
            group-hover:translate-x-0
            transition-all duration-300
          "
              >
                Launch Module <span className="ml-2">→</span>
              </div>
            </div>
          </Link>
        ))}
      </div>


      <footer className="p-8 rounded-3xl glass-card flex flex-col md:flex-row items-center justify-between gap-6 border-zinc-800/30">
        <div className="flex items-center gap-4">
          <div className={`w-3 h-3 rounded-full ${hasKey ? "bg-emerald-500 shadow-[0_0_12px_rgba(16,185,129,0.5)]" : "bg-red-500 shadow-[0_0_12px_rgba(239,68,68,0.5)]"}`} />
          <div>
            <span className="text-sm font-semibold flex items-center gap-2">
              <span className="material-symbols-outlined text-xs">database</span>
              Backend Status
            </span>
            <p className="text-xs text-zinc-500">
              {hasKey ? "API Connection established" : "Missing BACKBOARD_API_KEY environment variable"}
            </p>
          </div>
        </div>
        {!hasKey && (
          <Link href="/settings" className="btn-primary py-2.5">
            Fix Configuration
          </Link>
        )}
      </footer>
    </div>
  );
}
