import React from "react";
import {
  CheckCircle2,
  Loader2,
  Circle,
  FileCheck,
  Search,
  ShieldCheck,
  Globe,
  Gauge,
  Sparkles,
} from "lucide-react";

export interface ScanStage {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}

export const SCAN_STAGES: ScanStage[] = [
  {
    id: "input_received",
    name: "Input received",
    description: "Payload captured, sanitized, and defanged",
    icon: FileCheck,
  },
  {
    id: "indicators_extracted",
    name: "Indicators extracted",
    description: "Parsing domains, IP addresses, syntax tokens & URIs",
    icon: Search,
  },
  {
    id: "security_rules_checked",
    name: "Security rules checked",
    description: "Evaluating against heuristics & brand-spoof patterns",
    icon: ShieldCheck,
  },
  {
    id: "threat_intelligence",
    name: "Threat intelligence",
    description: "Cross-referencing IOC databases & reputation caches",
    icon: Globe,
  },
  {
    id: "risk_assessment",
    name: "Risk assessment",
    description: "Calculating severity score & multi-factor confidence index",
    icon: Gauge,
  },
  {
    id: "ai_explanation",
    name: "AI explanation",
    description: "Synthesizing executive summary & analyst reasoning",
    icon: Sparkles,
  },
];

export interface ScanProgressProps {
  currentStageIndex: number; // 0 to 6 (6 = all complete)
  targetName?: string;
}

export const ScanProgress: React.FC<ScanProgressProps> = ({
  currentStageIndex,
  targetName,
}) => {
  const percent = Math.min(100, Math.round((currentStageIndex / SCAN_STAGES.length) * 100));

  return (
    <div
      role="status"
      aria-live="polite"
      className="p-6 rounded-2xl bg-xerox-surface border border-xerox-border space-y-6"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-xerox-border-subtle pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-xerox-red animate-ping" />
            <h3 className="text-sm font-mono font-bold text-white tracking-wider uppercase">
              Heuristic Inspection In Progress
            </h3>
          </div>
          {targetName && (
            <p className="text-xs font-mono text-slate-400 mt-1 truncate max-w-md">
              Target: <span className="text-slate-200">{targetName}</span>
            </p>
          )}
        </div>
        <div className="text-right font-mono">
          <span className="text-xs text-slate-400">PIPELINE COMPLETION: </span>
          <span className="text-sm font-bold text-xerox-red">{percent}%</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="relative w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-red-600 to-red-400 transition-all duration-300 shadow-red-glow"
          style={{ width: `${percent}%` }}
        />
      </div>

      {/* 6 Security Stages List */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {SCAN_STAGES.map((stage, idx) => {
          const isComplete = idx < currentStageIndex;
          const isActive = idx === currentStageIndex;
          const Icon = stage.icon;

          return (
            <div
              key={stage.id}
              className={`flex items-start gap-3 p-3.5 rounded-xl border transition-all duration-200 ${
                isActive
                  ? "bg-red-500/10 border-red-500/40 shadow-[0_0_15px_rgba(239,68,68,0.15)]"
                  : isComplete
                  ? "bg-emerald-500/5 border-emerald-500/20"
                  : "bg-xerox-surface/60 border-xerox-border-subtle opacity-50"
              }`}
            >
              <div className="mt-0.5">
                {isComplete ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                ) : isActive ? (
                  <Loader2 className="w-4 h-4 text-xerox-red animate-spin" />
                ) : (
                  <Circle className="w-4 h-4 text-slate-600" />
                )}
              </div>

              <div className="space-y-0.5 min-w-0">
                <div className="flex items-center gap-1.5">
                  <Icon
                    className={`w-3.5 h-3.5 ${
                      isActive ? "text-xerox-red" : isComplete ? "text-emerald-400" : "text-slate-500"
                    }`}
                  />
                  <h4
                    className={`text-xs font-mono font-bold truncate ${
                      isActive ? "text-white" : isComplete ? "text-slate-200" : "text-slate-500"
                    }`}
                  >
                    {stage.name}
                  </h4>
                </div>
                <p className="text-[11px] text-slate-400 line-clamp-1 font-sans">
                  {stage.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
