export default function SettingsPage() {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header className="space-y-2">
        <h2 className="text-3xl font-extrabold tracking-tight text-white">System Settings</h2>
        <p className="text-zinc-400">
          Configure authentication protocols and global environment parameters.
        </p>
      </header>

      <div className="glass-card p-8 rounded-3xl space-y-8 max-w-2xl">
        <section className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="material-symbols-outlined text-zinc-400">key</div>
            <h3 className="text-lg font-bold">API Authentication</h3>
          </div>
          <p className="text-sm text-zinc-400 leading-relaxed">
            The Backboard API key must be injected via secure environment variables.
            For local development, ensure your <code className="text-indigo-400">.env.local</code> is correctly configured.
          </p>
        </section>

        <section className="space-y-4">
          <h4 className="text-xs font-bold uppercase tracking-widest text-zinc-500">Local Configuration Guide</h4>
          <div className="space-y-3">
            <div className="text-sm text-zinc-300">
              Create a <code className="bg-zinc-800 px-1.5 py-0.5 rounded font-mono text-zinc-400 text-[12px]">.env.local</code> file in your web root:
            </div>
            <div className="relative group">
              <pre className="bg-black/50 border border-zinc-800 p-4 rounded-2xl font-mono text-sm text-indigo-400 overflow-x-auto transition-colors group-hover:border-indigo-500/30">
                BACKBOARD_API_KEY=your_secure_credential_here
              </pre>
              <button className="absolute top-3 right-3 text-[10px] uppercase font-bold text-zinc-600 hover:text-white transition-colors">
                COPY
              </button>
            </div>
            <p className="text-[11px] text-zinc-500 italic">
              Note: Never commit your environment files to public version control.
            </p>
          </div>
        </section>

        <section className="pt-4 border-t border-zinc-800/50">
          <button className="btn-primary w-full py-3">
            Refresh Connection Status
          </button>
        </section>
      </div>
    </div>
  );
}
