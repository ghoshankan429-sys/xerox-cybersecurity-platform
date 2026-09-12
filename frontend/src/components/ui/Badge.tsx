import React from "react";

export type BadgeVariant = "default" | "safe" | "warning" | "danger" | "info" | "outline";
export type BadgeSize = "sm" | "md";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  size?: BadgeSize;
  icon?: React.ReactNode;
  children: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = "default",
  size = "md",
  icon,
  children,
  className = "",
  ...props
}) => {
  const variantStyles: Record<BadgeVariant, string> = {
    default:
      "bg-slate-800/80 text-slate-300 border-slate-700/60",
    safe:
      "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
    warning:
      "bg-amber-500/10 text-amber-400 border-amber-500/30",
    danger:
      "bg-red-500/15 text-red-400 border-red-500/30 shadow-[0_0_12px_rgba(239,68,68,0.2)]",
    info:
      "bg-blue-500/10 text-blue-400 border-blue-500/30",
    outline:
      "bg-transparent text-slate-300 border-xerox-border",
  };

  const sizeStyles: Record<BadgeSize, string> = {
    sm: "text-[10px] px-2 py-0.5 gap-1",
    md: "text-xs px-2.5 py-1 gap-1.5",
  };

  return (
    <span
      className={`inline-flex items-center font-mono font-semibold rounded-lg border tracking-wider select-none ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      {...props}
    >
      {icon && <span className="flex-shrink-0">{icon}</span>}
      <span>{children}</span>
    </span>
  );
};
