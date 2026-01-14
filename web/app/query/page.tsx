import QueryInterface from "../../components/QueryInterface";

export default function QueryPage() {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header className="space-y-2">
        <h2 className="text-3xl font-extrabold tracking-tight text-white">Assistant</h2>
        <p className="text-zinc-400">
          Direct interface with your distributed knowledge. This node powers the
          <code className="text-indigo-400 font-mono text-xs mx-1 bg-indigo-500/10 px-1 rounded">VSCode-Buddy</code> extension ecosystem.
        </p>
      </header>

      <QueryInterface />
    </div>
  );
}
