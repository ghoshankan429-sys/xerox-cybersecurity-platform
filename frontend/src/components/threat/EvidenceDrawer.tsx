"use client";

import React, { useState } from "react";
import { EvidenceItem } from "@/types/threat";
import { ChevronDown, ChevronUp, ShieldAlert, HelpCircle } from "lucide-react";

interface EvidenceDrawerProps {
  evidence: EvidenceItem[];
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({ evidence }) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0);

  if (!evidence || evidence.length === 0) {
    return (
      <div className="p-6 bg-surface rounded-2xl border border-surface-border text-center text-slate-400">
        No adverse telemetry flags recorded for this target.
      </div>
    );
  }

  const toggle = (idx: number) => {
    setExpandedIndex(expandedIndex === idx ? null : idx);
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "CRITICAL":
        return "bg-red-500/20 text-red-400 border-red-500/40";
      case "HIGH":
        return "bg-orange-500/20 text-orange-400 border-orange-500/40";
      case "MEDIUM":
        return "bg-amber-500/20 text-amber-400 border-amber-500/40";
      case "LOW":
        return "bg-cyan-500/20 text-cyan-400 border-cyan-500/40";
      default:
        return "bg-slate-700/50 text-slate-300 border-slate-600";
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-blue-400" />
          Technical Evidence & Forensic Indicators ({evidence.length})
        </h3>
        <span className="text-xs font-mono text-slate-400">
          DECONSTRUCTED TELEMETRY
        </span>
      </div>

      <div className="space-y-2">
        {evidence.map((item, idx) => {
          const isExpanded = expandedIndex === idx;
          return (
            <div
              key={idx}
              className="rounded-xl bg-surface border border-surface-border overflow-hidden transition-colors hover:border-slate-700"
            >
              <button
                onClick={() => toggle(idx)}
                className="w-full text-left p-4 flex items-center justify-between gap-4 cursor-pointer"
              >
                <div className="flex flex-wrap items-center gap-2.5 flex-1">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${getSeverityBadge(
                      item.severity
                    )}`}
                  >
                    {item.severity}
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-400 border border-slate-700">
                    {item.category}
                  </span>
                  <span className="text-sm font-semibold text-slate-200">
                    {item.title}
                  </span>
                </div>
                {isExpanded ? (
                  <ChevronUp className="w-4 h-4 text-slate-400 flex-shrink-0" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-slate-400 flex-shrink-0" />
                )}
              </button>

              {isExpanded && (
                <div className="px-4 pb-4 pt-1 space-y-3 border-t border-slate-800/80 bg-slate-950/40">
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {item.description}
                  </p>

                  {/* Technical Proof snippet */}
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 font-mono text-xs text-cyan-300 overflow-x-auto">
                    <span className="text-slate-500 select-none">$ TELEMETRY_PROOF: </span>
                    {item.technical_proof}
                  </div>

                  {/* Why this matters explanation */}
                  <div className="flex items-start gap-2 p-2.5 rounded-lg bg-blue-950/20 border border-blue-900/30 text-xs text-blue-200/90">
                    <HelpCircle className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <span className="font-semibold text-blue-300">Why this matters: </span>
                      {item.why_this_matters}
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
