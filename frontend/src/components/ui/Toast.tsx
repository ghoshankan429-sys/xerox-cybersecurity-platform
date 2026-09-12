import React, { createContext, useContext, useState, useCallback } from "react";
import { CheckCircle2, AlertTriangle, AlertCircle, Info, X } from "lucide-react";

export type ToastType = "success" | "error" | "warning" | "info";

export interface ToastItem {
  id: string;
  type: ToastType;
  title?: string;
  message: string;
}

interface ToastContextType {
  showToast: (toast: Omit<ToastItem, "id">) => void;
  success: (message: string, title?: string) => void;
  error: (message: string, title?: string) => void;
  warning: (message: string, title?: string) => void;
  info: (message: string, title?: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = useCallback(
    ({ type, title, message }: Omit<ToastItem, "id">) => {
      const id = Math.random().toString(36).substring(2, 9);
      setToasts((prev) => [...prev, { id, type, title, message }]);

      setTimeout(() => {
        removeToast(id);
      }, 5000);
    },
    [removeToast]
  );

  const success = useCallback(
    (message: string, title?: string) => showToast({ type: "success", title, message }),
    [showToast]
  );
  const error = useCallback(
    (message: string, title?: string) => showToast({ type: "error", title, message }),
    [showToast]
  );
  const warning = useCallback(
    (message: string, title?: string) => showToast({ type: "warning", title, message }),
    [showToast]
  );
  const info = useCallback(
    (message: string, title?: string) => showToast({ type: "info", title, message }),
    [showToast]
  );

  return (
    <ToastContext.Provider value={{ showToast, success, error, warning, info }}>
      {children}
      {/* Toast Overlay Container */}
      <div
        aria-live="polite"
        className="fixed bottom-5 right-5 z-50 flex flex-col gap-2.5 max-w-sm w-full pointer-events-none"
      >
        {toasts.map((toast) => {
          const configs = {
            success: {
              icon: <CheckCircle2 className="w-4 h-4 text-emerald-400" />,
              border: "border-emerald-500/40",
              bg: "bg-[#0d1614]/95",
            },
            error: {
              icon: <AlertCircle className="w-4 h-4 text-red-400" />,
              border: "border-red-500/40 shadow-[0_0_20px_rgba(239,68,68,0.2)]",
              bg: "bg-[#180f12]/95",
            },
            warning: {
              icon: <AlertTriangle className="w-4 h-4 text-amber-400" />,
              border: "border-amber-500/40",
              bg: "bg-[#18140f]/95",
            },
            info: {
              icon: <Info className="w-4 h-4 text-blue-400" />,
              border: "border-blue-500/40",
              bg: "bg-[#0f1418]/95",
            },
          }[toast.type];

          return (
            <div
              key={toast.id}
              role="alert"
              className={`pointer-events-auto flex items-start gap-3 p-4 rounded-xl border backdrop-blur-md shadow-2xl transition-all duration-300 animate-in slide-in-from-bottom-2 ${configs.bg} ${configs.border}`}
            >
              <div className="flex-shrink-0 mt-0.5">{configs.icon}</div>
              <div className="flex-1 space-y-0.5">
                {toast.title && (
                  <h5 className="text-xs font-mono font-bold text-white tracking-wide">
                    {toast.title}
                  </h5>
                )}
                <p className="text-xs text-slate-300 font-sans leading-relaxed">
                  {toast.message}
                </p>
              </div>
              <button
                onClick={() => removeToast(toast.id)}
                aria-label="Dismiss notification"
                className="text-slate-400 hover:text-white p-0.5 transition-colors"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = (): ToastContextType => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
};
