import React from "react";
import { ShieldCheck, CheckCircle2, AlertTriangle, ShieldAlert, AlertOctagon } from "lucide-react";
import { RiskLevel } from "@/types";

export interface RiskBadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  level: RiskLevel;
  score?: number;
  size?: "sm" | "md" | "lg";
  showIcon?: boolean;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  level,
  score,
  size = "md",
  showIcon = true,
  className = "",
  ...props
}) => {
  const config: Record<
    RiskLevel,
    {
      label: string;
      colorClass: string;
      icon: React.ReactNode;
      glowClass: string;
    }
  > = {
    BENIGN: {
      label: "BENIGN",
      colorClass: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
      icon: <ShieldCheck className="w-3.5 h-3.5 flex-shrink-0" />,
      glowClass: "shadow-[0_0_12px_rgba(16,185,129,0.15)]",
    },
    "LOW RISK": {
      label: "LOW RISK",
      colorClass: "bg-emerald-500/10 text-emerald-300 border-emerald-500/30",
      icon: <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0" />,
      glowClass: "",
    },
    SUSPICIOUS: {
      label: "SUSPICIOUS",
      colorClass: "bg-amber-500/15 text-amber-400 border-amber-500/30",
      icon: <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />,
      glowClass: "shadow-[0_0_15px_rgba(245,158,11,0.2)]",
    },
    "HIGH RISK": {
      label: "HIGH RISK",
      colorClass: "bg-red-500/15 text-red-400 border-red-500/40",
      icon: <ShieldAlert className="w-3.5 h-3.5 flex-shrink-0" />,
      glowClass: "shadow-[0_0_20px_rgba(239,68,68,0.25)]",
    },
    CRITICAL: {
      label: "CRITICAL",
      colorClass: "bg-red-600/20 text-red-300 border-red-500/50",
      icon: <AlertOctagon className="w-3.5 h-3.5 flex-shrink-0 animate-pulse" />,
      glowClass: "shadow-[0_0_25px_rgba(255,45,32,0.4)]",
    },
  };

  const item = config[level] || config["SUSPICIOUS"];

  const sizeStyles = {
    sm: "text-[10px] px-2 py-0.5 gap-1",
    md: "text-xs px-2.5 py-1 gap-1.5",
    lg: "text-sm px-3.5 py-1.5 gap-2 font-bold",
  };

  return (
    <span
      className={`inline-flex items-center font-mono font-semibold rounded-lg border tracking-wider select-none ${item.colorClass} ${item.glowClass} ${sizeStyles[size]} ${className}`}
      {...props}
    >
      {showIcon && item.icon}
      <span>{item.label}</span>
      {typeof score === "number" && (
        <span className="opacity-75 font-normal ml-0.5">({score}%)</span>
      )}
    </span>
  );
};
