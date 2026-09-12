"use client";

import React from "react";
import { RecommendedAction } from "@/types/threat";
import { ShieldCheck, AlertOctagon, KeyRound, Flag, CheckCircle2 } from "lucide-react";

interface RecommendedActionsProps {
  actions: RecommendedAction[];
}

export const RecommendedActions: React.FC<RecommendedActionsProps> = ({ actions }) => {
  if (!actions || actions.length === 0) {
    return null;
  }

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case "IMMEDIATE":
        return "bg-red-500/20 text-red-400 border-red-500/40";
      case "PREVENTATIVE":
        return "bg-blue-500/20 text-blue-400 border-blue-500/40";
      default:
        return "bg-slate-700/50 text-slate-300 border-slate-600";
    }
  };

  const getActionIcon = (actionType: string) => {
    switch (actionType) {
      case "DO_NOT_CLICK":
        return <AlertOctagon className="w-4 h-4 text-red-400" />;
      case "CHANGE_PASSWORD":
        return <KeyRound className="w-4 h-4 text-amber-400" />;
      case "REPORT_PHISHING":
        return <Flag className="w-4 h-4 text-purple-400" />;
      case "SAFE_TO_PROCEED":
        return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
      default:
        return <ShieldCheck className="w-4 h-4 text-blue-400" />;
    }
  };

  return (
    <div className="p-5 bg-surface rounded-2xl border border-surface-border space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-base font-bold text-slate-100 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          Recommended Response Playbook
        </h4>
        <span className="text-xs font-mono text-slate-400">ACTION DIRECTIVES</span>
      </div>

      <div className="space-y-2.5">
        {actions.map((act, idx) => (
          <div
            key={idx}
            className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-start gap-3 hover:border-slate-700 transition-colors"
          >
            <div className="mt-0.5 p-1.5 rounded-lg bg-slate-800/80 border border-slate-700">
              {getActionIcon(act.action_type)}
            </div>
            <div className="flex-1 space-y-1">
              <div className="flex items-center gap-2">
                <span
                  className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-bold border ${getPriorityBadge(
                    act.priority
                  )}`}
                >
                  {act.priority}
                </span>
                <span className="text-sm font-semibold text-slate-200">{act.action}</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">{act.rationale}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
