import React from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "./Button";

export interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  action?: React.ReactNode;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = "Telemetry Fault Detected",
  message,
  onRetry,
  action,
}) => {
  return (
    <div
      role="alert"
      className="p-6 sm:p-8 rounded-2xl bg-red-950/20 border border-red-500/30 flex flex-col items-center justify-center text-center space-y-4"
    >
      <div className="w-12 h-12 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-400 shadow-[0_0_20px_rgba(239,68,68,0.2)]">
        <AlertTriangle className="w-6 h-6" />
      </div>

      <div className="space-y-1 max-w-md">
        <h4 className="text-sm font-bold text-red-200 tracking-tight">
          {title}
        </h4>
        <p className="text-xs text-red-300/80 font-mono leading-relaxed">
          {message}
        </p>
      </div>

      {onRetry && (
        <Button
          variant="outline"
          size="sm"
          onClick={onRetry}
          leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
          className="border-red-500/30 hover:border-red-500/60 text-red-300"
        >
          RETRY OPERATION
        </Button>
      )}

      {!onRetry && action && <div>{action}</div>}
    </div>
  );
};
