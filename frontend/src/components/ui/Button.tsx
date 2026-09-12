import React, { forwardRef } from "react";
import { Loader2 } from "lucide-react";

export type ButtonVariant = "primary" | "secondary" | "outline" | "ghost" | "danger";
export type ButtonSize = "sm" | "md" | "lg";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  loadingText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = "primary",
      size = "md",
      loading = false,
      loadingText,
      leftIcon,
      rightIcon,
      fullWidth = false,
      disabled,
      className = "",
      type = "button",
      ...props
    },
    ref
  ) => {
    const baseStyles =
      "inline-flex items-center justify-center font-mono font-medium rounded-xl transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-xerox-red focus-visible:ring-offset-2 focus-visible:ring-offset-xerox-bg disabled:opacity-50 disabled:pointer-events-none select-none";

    const variantStyles: Record<ButtonVariant, string> = {
      primary:
        "bg-xerox-red hover:bg-xerox-red-bright text-white shadow-red-glow hover:shadow-red-glow-lg border border-red-500/40 active:scale-[0.98]",
      secondary:
        "bg-xerox-surface hover:bg-xerox-surface-elevated text-slate-200 border border-xerox-border hover:border-xerox-border-highlight active:scale-[0.98]",
      outline:
        "bg-transparent hover:bg-xerox-surface text-slate-200 border border-xerox-border hover:border-slate-500 active:scale-[0.98]",
      ghost:
        "bg-transparent hover:bg-xerox-surface text-slate-400 hover:text-slate-100 border border-transparent active:scale-[0.98]",
      danger:
        "bg-red-950/60 hover:bg-red-900/80 text-red-400 border border-red-600/40 shadow-sm active:scale-[0.98]",
    };

    const sizeStyles: Record<ButtonSize, string> = {
      sm: "text-xs px-3 py-1.5 gap-1.5 h-8",
      md: "text-xs sm:text-sm px-4 py-2.5 gap-2 h-10",
      lg: "text-sm sm:text-base px-6 py-3.5 gap-2.5 h-12 font-semibold tracking-wide",
    };

    const widthStyle = fullWidth ? "w-full" : "";

    return (
      <button
        ref={ref}
        type={type}
        disabled={disabled || loading}
        className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${widthStyle} ${className}`}
        aria-busy={loading}
        {...props}
      >
        {loading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin flex-shrink-0" aria-hidden="true" />
            <span>{loadingText || children}</span>
          </>
        ) : (
          <>
            {leftIcon && <span className="flex-shrink-0" aria-hidden="true">{leftIcon}</span>}
            <span>{children}</span>
            {rightIcon && <span className="flex-shrink-0" aria-hidden="true">{rightIcon}</span>}
          </>
        )}
      </button>
    );
  }
);

Button.displayName = "Button";
