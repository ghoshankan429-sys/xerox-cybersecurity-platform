import React, { useEffect, useRef } from "react";
import { X } from "lucide-react";
import { IconButton } from "./IconButton";

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: React.ReactNode;
  description?: string;
  children: React.ReactNode;
  maxWidth?: "sm" | "md" | "lg" | "xl";
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  description,
  children,
  maxWidth = "md",
}) => {
  const modalRef = useRef<HTMLDivElement>(null);

  // Close on Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    if (isOpen) {
      document.addEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "unset";
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const maxWidthStyles = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-2xl",
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      {/* Backdrop */}
      <div
        onClick={onClose}
        className="fixed inset-0 bg-black/80 backdrop-blur-sm transition-opacity duration-200"
        aria-hidden="true"
      />

      {/* Modal Dialog Body */}
      <div
        ref={modalRef}
        className={`relative w-full ${maxWidthStyles[maxWidth]} rounded-2xl bg-xerox-surface border border-xerox-border p-6 shadow-2xl z-10 space-y-4 animate-in fade-in zoom-in-95 duration-150`}
      >
        <div className="flex items-start justify-between gap-4 border-b border-xerox-border-subtle pb-4">
          <div className="space-y-1">
            {title && (
              <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                {title}
              </h2>
            )}
            {description && (
              <p className="text-xs text-slate-400 font-sans">
                {description}
              </p>
            )}
          </div>
          <IconButton
            icon={<X className="w-4 h-4" />}
            aria-label="Close dialog"
            size="sm"
            onClick={onClose}
            className="text-slate-400 hover:text-white"
          />
        </div>

        <div>{children}</div>
      </div>
    </div>
  );
};
