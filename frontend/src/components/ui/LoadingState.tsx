import React from "react";
import { Cpu } from "lucide-react";

export interface LoadingStateProps {
  message?: string;
  subMessage?: string;
  size?: "sm" | "md" | "lg";
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = "INITIALIZING DEFENSIVE TELEMETRY...",
  subMessage,
  size = "md",
}) => {
  const sizeStyles = {
    sm: "py-6",
    md: "py-12",
    lg: "py-20",
  };

  return (
    <div
      role="status"
      aria-live="polite"
      className={`flex flex-col items-center justify-center text-center space-y-4 ${sizeStyles[size]}`}
    >
      <div className="relative">
        <div className="w-12 h-12 rounded-xl bg-xerox-surface border border-xerox-border flex items-center justify-center shadow-panel">
          <Cpu className="w-6 h-6 text-xerox-red animate-pulse" />
        </div>
        <div className="absolute -inset-1 rounded-xl border border-red-500/30 animate-ping opacity-30 pointer-events-none" />
      </div>

      <div className="space-y-1">
        <p className="text-xs font-mono font-semibold text-slate-300 tracking-wider">
          {message}
        </p>
        {subMessage && (
          <p className="text-[11px] font-mono text-slate-500">
            {subMessage}
          </p>
        )}
      </div>
    </div>
  );
};
