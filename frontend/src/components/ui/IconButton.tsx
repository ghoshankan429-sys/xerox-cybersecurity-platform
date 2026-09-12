import React, { forwardRef } from "react";
import { ButtonVariant, ButtonSize } from "./Button";

export interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  "aria-label": string;
  icon: React.ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  tooltip?: string;
}

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  (
    {
      icon,
      variant = "ghost",
      size = "md",
      tooltip,
      className = "",
      type = "button",
      "aria-label": ariaLabel,
      ...props
    },
    ref
  ) => {
    const baseStyles =
      "inline-flex items-center justify-center rounded-xl transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-xerox-red focus-visible:ring-offset-2 focus-visible:ring-offset-xerox-bg disabled:opacity-50 disabled:pointer-events-none select-none";

    const variantStyles: Record<ButtonVariant, string> = {
      primary:
        "bg-xerox-red hover:bg-xerox-red-bright text-white shadow-red-glow border border-red-500/40 active:scale-95",
      secondary:
        "bg-xerox-surface hover:bg-xerox-surface-elevated text-slate-200 border border-xerox-border hover:border-xerox-border-highlight active:scale-95",
      outline:
        "bg-transparent hover:bg-xerox-surface text-slate-300 border border-xerox-border hover:border-slate-500 active:scale-95",
      ghost:
        "bg-transparent hover:bg-xerox-surface text-slate-400 hover:text-slate-100 border border-transparent active:scale-95",
      danger:
        "bg-red-950/60 hover:bg-red-900/80 text-red-400 border border-red-600/40 active:scale-95",
    };

    const sizeStyles: Record<ButtonSize, string> = {
      sm: "w-8 h-8 p-1.5",
      md: "w-10 h-10 p-2",
      lg: "w-12 h-12 p-3",
    };

    return (
      <button
        ref={ref}
        type={type}
        aria-label={ariaLabel}
        title={tooltip || ariaLabel}
        className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
        {...props}
      >
        {icon}
      </button>
    );
  }
);

IconButton.displayName = "IconButton";
