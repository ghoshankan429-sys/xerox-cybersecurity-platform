import React, { forwardRef, useId } from "react";
import { AlertCircle } from "lucide-react";

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
  showCharCount?: boolean;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  (
    {
      label,
      error,
      helperText,
      showCharCount,
      maxLength,
      value,
      id: customId,
      className = "",
      disabled,
      ...props
    },
    ref
  ) => {
    const generatedId = useId();
    const id = customId || generatedId;
    const errorId = `${id}-error`;
    const helperId = `${id}-helper`;

    const charCount = typeof value === "string" ? value.length : 0;

    return (
      <div className="w-full space-y-1.5">
        <div className="flex items-center justify-between">
          {label && (
            <label
              htmlFor={id}
              className="block text-xs font-mono font-semibold text-slate-300 tracking-wider uppercase"
            >
              {label}
            </label>
          )}
          {showCharCount && maxLength && (
            <span className="text-[11px] font-mono text-slate-500">
              {charCount} / {maxLength}
            </span>
          )}
        </div>
        <textarea
          ref={ref}
          id={id}
          value={value}
          maxLength={maxLength}
          disabled={disabled}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? errorId : helperText ? helperId : undefined}
          className={`w-full p-4 rounded-xl bg-xerox-surface border text-sm text-slate-100 placeholder-slate-500 font-sans transition-all duration-200 outline-none focus:ring-2 focus:ring-xerox-red/60 focus:border-xerox-red disabled:opacity-50 disabled:bg-slate-900/50 disabled:cursor-not-allowed resize-y min-h-[120px] ${
            error
              ? "border-red-500/80 bg-red-950/10 focus:ring-red-500"
              : "border-xerox-border hover:border-xerox-border-highlight"
          } ${className}`}
          {...props}
        />
        {error && (
          <p
            id={errorId}
            role="alert"
            className="text-xs font-mono text-red-400 flex items-center gap-1.5 mt-1"
          >
            <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" aria-hidden="true" />
            <span>{error}</span>
          </p>
        )}
        {!error && helperText && (
          <p id={helperId} className="text-xs font-mono text-slate-400 mt-1">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Textarea.displayName = "Textarea";
