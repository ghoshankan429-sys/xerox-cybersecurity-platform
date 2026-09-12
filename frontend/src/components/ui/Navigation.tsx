"use client";

import React from "react";
import { Shield, Radio, Terminal, History, BarChart2 } from "lucide-react";

interface NavigationProps {
  activeView: "scanner" | "history" | "dashboard";
  onSelectView: (view: "scanner" | "history" | "dashboard") => void;
  totalHistoryCount?: number;
}

export const Navigation: React.FC<NavigationProps> = ({
  activeView,
  onSelectView,
  totalHistoryCount = 0,
}) => {
  return (
    <header className="border-b border-surface-border bg-canvas/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo & Robot Icon */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => onSelectView("scanner")}>
          <div className="w-10 h-10 rounded-xl bg-slate-900 border border-brand-primary/40 flex items-center justify-center relative shadow-[0_0_15px_rgba(59,130,246,0.3)]">
            <Shield className="w-5 h-5 text-brand-primary" />
            <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500" />
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-black tracking-wider text-white font-mono">XEROX</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                v1.0 CO-PILOT
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono tracking-tight">
              AUTONOMOUS THREAT INTELLIGENCE
            </p>
          </div>
        </div>

        {/* View Switcher */}
        <nav className="flex items-center gap-1 p-1 rounded-xl bg-slate-900/90 border border-slate-800">
          <button
            onClick={() => onSelectView("scanner")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
              activeView === "scanner"
                ? "bg-brand-primary text-white shadow-md shadow-blue-500/20"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            Scanner
          </button>
          <button
            onClick={() => onSelectView("history")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
              activeView === "history"
                ? "bg-brand-primary text-white shadow-md shadow-blue-500/20"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <History className="w-3.5 h-3.5" />
            History
            {totalHistoryCount > 0 && (
              <span className="ml-0.5 px-1.5 py-0.2 rounded-full text-[10px] bg-slate-800 text-slate-300">
                {totalHistoryCount}
              </span>
            )}
          </button>
          <button
            onClick={() => onSelectView("dashboard")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
              activeView === "dashboard"
                ? "bg-brand-primary text-white shadow-md shadow-blue-500/20"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <BarChart2 className="w-3.5 h-3.5" />
            Dashboard
          </button>
        </nav>

        {/* Status indicator */}
        <div className="hidden md:flex items-center gap-2 font-mono text-xs text-slate-400">
          <Radio className="w-4 h-4 text-emerald-400 animate-pulse" />
          <span>RADAR ARMED</span>
        </div>
      </div>
    </header>
  );
};
