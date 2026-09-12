"use client";

import React, { useState } from "react";
import { TargetType } from "@/types/threat";
import { Globe, MessageSquare, Mail, Camera, ArrowRight, Sparkles, Loader2 } from "lucide-react";

interface UnifiedScannerProps {
  onScanUrl: (url: string) => void;
  onScanMessage: (content: string, sender?: string) => void;
  isLoading: boolean;
}

export const UnifiedScanner: React.FC<UnifiedScannerProps> = ({
  onScanUrl,
  onScanMessage,
  isLoading,
}) => {
  const [activeTab, setActiveTab] = useState<TargetType>("URL");
  const [urlInput, setUrlInput] = useState("");
  const [messageInput, setMessageInput] = useState("");
  const [senderInput, setSenderInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoading) return;

    if (activeTab === "URL" && urlInput.trim()) {
      onScanUrl(urlInput.trim());
    } else if (activeTab === "MESSAGE" && messageInput.trim()) {
      onScanMessage(messageInput.trim(), senderInput.trim() || undefined);
    }
  };

  const handleSetDemo = (type: "apple" | "sms" | "safe") => {
    if (type === "apple") {
      setActiveTab("URL");
      setUrlInput("https://apple-id-verify.support-secure.live/auth");
    } else if (type === "sms") {
      setActiveTab("MESSAGE");
      setMessageInput(
        "URGENT ALERT: Your Chase account has been temporarily restricted due to anomalous transactions. Restore access within 24h: hxxps://chase-account-restore[.]xyz"
      );
      setSenderInput("+1 (800) 555-0199");
    } else if (type === "safe") {
      setActiveTab("URL");
      setUrlInput("https://github.com");
    }
  };

  return (
    <div className="bg-surface rounded-2xl border border-surface-border p-6 shadow-xl space-y-5">
      {/* Mode Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900 border border-slate-800">
          <button
            type="button"
            onClick={() => setActiveTab("URL")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
              activeTab === "URL"
                ? "bg-brand-primary text-white shadow-lg shadow-blue-500/20"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Globe className="w-3.5 h-3.5" />
            URL / Link
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("MESSAGE")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
              activeTab === "MESSAGE"
                ? "bg-brand-primary text-white shadow-lg shadow-blue-500/20"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            Message / SMS
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("EMAIL")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
              activeTab === "EMAIL"
                ? "bg-brand-primary text-white shadow-lg shadow-blue-500/20"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Mail className="w-3.5 h-3.5" />
            Email Header
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("SCREENSHOT")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
              activeTab === "SCREENSHOT"
                ? "bg-brand-primary text-white shadow-lg shadow-blue-500/20"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Camera className="w-3.5 h-3.5" />
            Screenshot
          </button>
        </div>

        {/* Quick Demo Payloads */}
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span className="text-[11px] font-mono text-slate-500">TEST CASES:</span>
          <button
            type="button"
            onClick={() => handleSetDemo("apple")}
            className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-xs text-red-300 hover:bg-red-950/30 hover:border-red-800/60 transition-colors"
          >
            Apple Phish
          </button>
          <button
            type="button"
            onClick={() => handleSetDemo("sms")}
            className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-xs text-amber-300 hover:bg-amber-950/30 hover:border-amber-800/60 transition-colors"
          >
            Urgent SMS
          </button>
          <button
            type="button"
            onClick={() => handleSetDemo("safe")}
            className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-xs text-emerald-300 hover:bg-emerald-950/30 hover:border-emerald-800/60 transition-colors"
          >
            Safe Target
          </button>
        </div>
      </div>

      {/* Input Forms */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {activeTab === "URL" && (
          <div className="space-y-2">
            <label className="text-xs font-mono text-slate-400">
              TARGET URL, DOMAIN, OR SHORTENED LINK
            </label>
            <div className="relative">
              <input
                type="text"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="e.g. hxxps://apple-id-verify.support-secure.live/auth or bit.ly/3XyZ..."
                className="w-full px-4 py-3.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono text-sm placeholder-slate-600 focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary"
                disabled={isLoading}
              />
            </div>
          </div>
        )}

        {activeTab === "MESSAGE" && (
          <div className="space-y-3">
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-400">
                MESSAGE / SMS CONTENT (PASTE RAW TEXT)
              </label>
              <textarea
                rows={3}
                value={messageInput}
                onChange={(e) => setMessageInput(e.target.value)}
                placeholder="Paste the suspicious text message, WhatsApp alert, or urgent communication..."
                className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono text-sm placeholder-slate-600 focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary"
                disabled={isLoading}
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-mono text-slate-400">
                SENDER PHONE / ALPHA TAG (OPTIONAL)
              </label>
              <input
                type="text"
                value={senderInput}
                onChange={(e) => setSenderInput(e.target.value)}
                placeholder="e.g. +18005550199 or 'USPS-ALERT'"
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 font-mono text-xs placeholder-slate-600 focus:outline-none focus:border-brand-primary"
                disabled={isLoading}
              />
            </div>
          </div>
        )}

        {activeTab === "EMAIL" && (
          <div className="p-8 border-2 border-dashed border-slate-800 rounded-xl text-center space-y-2 bg-slate-950/40">
            <Mail className="w-8 h-8 text-slate-500 mx-auto" />
            <p className="text-sm text-slate-300 font-semibold">Drop raw .eml file or paste headers</p>
            <p className="text-xs text-slate-500">
              Parses SPF, DKIM, DMARC, and origin IP headers. Phase 1 active preview.
            </p>
          </div>
        )}

        {activeTab === "SCREENSHOT" && (
          <div className="p-8 border-2 border-dashed border-slate-800 rounded-xl text-center space-y-2 bg-slate-950/40">
            <Camera className="w-8 h-8 text-slate-500 mx-auto" />
            <p className="text-sm text-slate-300 font-semibold">
              Drop screenshot or press <kbd className="px-1.5 py-0.5 rounded bg-slate-800 text-xs">Ctrl+V</kbd>
            </p>
            <p className="text-xs text-slate-500">
              Vision OCR extracts embedded QR codes and spoofed brand logos.
            </p>
          </div>
        )}

        {/* Scan Engage Button */}
        <div className="flex items-center justify-between pt-2">
          <div className="text-xs text-slate-500 font-mono hidden sm:block">
            STRICT PRIVACY: Telemetry is evaluated non-destructively. Defanged output.
          </div>
          <button
            type="submit"
            disabled={
              isLoading ||
              (activeTab === "URL" && !urlInput.trim()) ||
              (activeTab === "MESSAGE" && !messageInput.trim()) ||
              activeTab === "EMAIL" ||
              activeTab === "SCREENSHOT"
            }
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-brand-primary hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-blue-500/25 transition-all"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                ENGAGING ANALYSIS...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                ENGAGE SENTINEL SCAN
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
