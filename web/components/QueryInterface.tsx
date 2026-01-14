"use client";

import React, { useState, useRef, useEffect } from "react";
import { API } from "../lib/api";

export default function QueryInterface() {
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<
    { role: "user" | "assistant"; text: string }[]
  >([]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  async function send() {
    if (!prompt.trim()) return;
    const userMsg = { role: "user" as const, text: prompt };
    setMessages((m) => [...m, userMsg]);
    setPrompt("");
    setLoading(true);

    try {
      const reply = await API.query(prompt);
      setMessages((m) => [
        ...m,
        { role: "assistant", text: reply },
      ]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "assistant", text: "Critical error connecting to Backboard API. Please check your network connection." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-[60vh] md:h-[70vh] glass-card rounded-3xl overflow-hidden border-zinc-800/50 shadow-2xl animate-in zoom-in-95 duration-500">
      {/* Header */}
      <div className="p-4 border-b border-zinc-800/50 bg-zinc-900/30 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-sm font-bold uppercase tracking-wider text-zinc-400 font-mono">Status</span>
        </div>
        <div className="text-xs text-zinc-500">
          {messages.length} messages in memory
        </div>
      </div>

      {/* Message Area */}
      <div ref={scrollRef} className="flex-1 overflow-auto p-6 space-y-6 scroll-smooth">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-40">
            <div className="material-symbols-outlined text-6xl">smart_toy</div>
            <div className="max-w-xs space-y-2">
              <h4 className="font-bold">Assistant Ready</h4>
              <p className="text-xs">Ask anything about your team's documents, meeting notes, or codebase history.</p>
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] p-4 rounded-2xl text-sm leading-relaxed ${m.role === "user"
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/20"
                : "bg-zinc-800/50 border border-zinc-700/50 text-zinc-200"
                }`}
            >
              {m.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-zinc-800/50 border border-zinc-700/50 p-4 rounded-2xl">
              <div className="flex gap-1">
                <div className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce" />
                <div className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce [animation-delay:0.2s]" />
                <div className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce [animation-delay:0.4s]" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-zinc-900/40 border-t border-zinc-800/50">
        <div className="relative flex items-center gap-3">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
            placeholder="Type your query..."
            rows={1}
            className="flex-1 bg-zinc-950 border border-zinc-800 rounded-2xl py-3 px-4 text-sm focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all outline-none resize-none"
          />
          <button
            onClick={send}
            disabled={loading || !prompt.trim()}
            className="btn-primary h-11 w-11 p-0 flex items-center justify-center rounded-full shrink-0"
          >
            <span className="material-symbols-outlined">send</span>
          </button>
        </div>
        <div className="mt-3 text-[10px] text-center text-zinc-600 font-medium uppercase tracking-tighter">
          Assistant utilizes distributed context nodes from Drive & Telegram
        </div>
      </div>
    </div>
  );
}
