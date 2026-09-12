import React from "react";
import { ShieldCheck } from "lucide-react";

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  action?: React.ReactNode;
  showSentinel?: boolean;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
  showSentinel = false,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 sm:p-12 text-center rounded-2xl bg-xerox-surface/50 border border-xerox-border-subtle">
      {showSentinel ? (
        <div className="relative mb-5">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-red-600/20 to-red-950/40 border border-red-500/30 flex items-center justify-center shadow-[0_0_25px_rgba(239,68,68,0.15)]">
            <ShieldCheck className="w-8 h-8 text-red-500" />
          </div>
          <span className="absolute -top-1 -right-1 flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500" />
          </span>
        </div>
      ) : (
        <div className="p-3.5 rounded-xl bg-xerox-surface border border-xerox-border mb-4 text-slate-400">
          {icon || <ShieldCheck className="w-6 h-6 text-slate-500" />}
        </div>
      )}

      <h4 className="text-base font-bold text-slate-200 tracking-tight mb-1.5">
        {title}
      </h4>
      <p className="text-xs text-slate-400 max-w-sm font-sans mb-6 leading-relaxed">
        {description}
      </p>

      {action && <div>{action}</div>}
    </div>
  );
};
