"use client";

import React from "react";
import { RedirectHop } from "@/types/threat";
import { GitCommit, Clock } from "lucide-react";

interface RedirectTreeProps {
  hops: RedirectHop[];
}

export const RedirectTree: React.FC<RedirectTreeProps> = ({ hops }) => {
  if (!hops || hops.length === 0) {
    return null;
  }

  const getStatusBadge = (code: number) => {
    if (code >= 200 && code < 300) {
      return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
    }
    if (code >= 300 && code < 400) {
      return "bg-cyan-500/20 text-cyan-400 border-cyan-500/30";
    }
    return "bg-red-500/20 text-red-400 border-red-500/30";
  };

  return (
    <div className="p-5 bg-surface rounded-2xl border border-surface-border space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-bold text-slate-200 flex items-center gap-2">
          <GitCommit className="w-4 h-4 text-cyan-400" />
          HTTP Redirection Cascade ({hops.length} Hops)
        </h4>
        <span className="text-[11px] font-mono text-slate-400">NETWORK TRACE</span>
      </div>

      <div className="space-y-2 relative before:absolute before:left-3 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-800">
        {hops.map((hop, idx) => (
          <div key={idx} className="relative flex items-start gap-3 pl-8 py-1.5">
            <div className="absolute left-1.5 top-3 w-3.5 h-3.5 rounded-full bg-slate-900 border-2 border-cyan-500 flex items-center justify-center -translate-x-1/2" />
            <div className="flex-1 p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs font-mono space-y-1">
              <div className="flex items-center justify-between gap-2">
                <span className="text-slate-400 font-semibold">Hop #{hop.hop_number}</span>
                <div className="flex items-center gap-2">
                  {hop.response_time_ms !== undefined && (
                    <span className="text-[10px] text-slate-500 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {hop.response_time_ms}ms
                    </span>
                  )}
                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] font-bold border ${getStatusBadge(
                      hop.status_code
                    )}`}
                  >
                    HTTP {hop.status_code}
                  </span>
                </div>
              </div>
              <div className="text-slate-300 break-all font-mono">
                {hop.to_url}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
