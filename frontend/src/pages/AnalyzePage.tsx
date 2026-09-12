import React, { useState } from "react";
import {
  Globe,
  Mail,
  ArrowRight,
  AlertTriangle,
  Cpu,
} from "lucide-react";
import { scanUrl, scanMessage } from "@/services/api";
import { ThreatReport, SentinelState } from "@/types";
import { SentinelRobotHUD } from "@/components/sentinel/SentinelRobotHUD";
import { getRiskColor } from "@/lib/utils";

export const AnalyzePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"URL" | "MESSAGE">("URL");
  const [inputValue, setInputValue] = useState("");
  const [senderMetadata, setSenderMetadata] = useState("");
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<ThreatReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sentinelState, setSentinelState] = useState<SentinelState>("IDLE");

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    setLoading(true);
    setError(null);
    setSentinelState("SCANNING");

    try {
      let result: ThreatReport;
      if (activeTab === "URL") {
        result = await scanUrl(inputValue.trim());
      } else {
        result = await scanMessage(inputValue.trim(), senderMetadata.trim() || undefined);
      }
      setReport(result);
      if (result.risk_score >= 70) {
        setSentinelState("ALERT");
      } else if (result.risk_score <= 25) {
        setSentinelState("VERIFIED");
      } else {
        setSentinelState("IDLE");
      }
    } catch (err: any) {
      setError(err.message || "Threat investigation failed. Please verify the target and try again.");
      setSentinelState("IDLE");
    } finally {
      setLoading(false);
    }
  };

  const sampleTargets = {
    URL: [
      {
        label: "Phishing: Fake Apple ID",
        val: "https://apple-id-verify.support-secure.live/auth",
      },
      {
        label: "Verified Safe: GitHub Portal",
        val: "https://github.com",
      },
    ],
    MESSAGE: [
      {
        label: "Smishing: Fake Postal Customs Fee",
        val: "USPS Alert: Your package has an unpaid customs charge of $2.49. Delivery cancelled within 12 hours: hxxps://usps-redelivery-support[.]xyz",
      },
      {
        label: "Benign: Team Project Update",
        val: "Hi team, the pull request for the security telemetry backend has been merged into main. Please review the updated documentation.",
      },
    ],
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Sentinel HUD Diagnostic Visualizer */}
      <SentinelRobotHUD
        state={sentinelState}
        riskLevel={report?.risk_level}
        riskScore={report?.risk_score}
        targetPreview={report?.defanged_target || (inputValue ? inputValue.slice(0, 80) : undefined)}
      />

      {/* Target Submission Workspace */}
      <div className="rounded-2xl bg-[#12141a] border border-[#222733] p-6 shadow-xl space-y-6">
        {/* Mode Selector Tabs */}
        <div className="flex items-center gap-2 border-b border-[#1e222d] pb-4">
          <button
            onClick={() => {
              setActiveTab("URL");
              setReport(null);
              setError(null);
            }}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-mono font-bold tracking-wide transition-all ${
              activeTab === "URL"
                ? "bg-red-600/15 text-red-400 border border-red-500/40 shadow-[0_0_15px_rgba(239,68,68,0.2)]"
                : "text-slate-400 hover:text-slate-200 hover:bg-[#181b24] border border-transparent"
            }`}
          >
            <Globe className="w-4 h-4" />
            URL / DOMAIN INSPECTOR
          </button>
          <button
            onClick={() => {
              setActiveTab("MESSAGE");
              setReport(null);
              setError(null);
            }}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-mono font-bold tracking-wide transition-all ${
              activeTab === "MESSAGE"
                ? "bg-red-600/15 text-red-400 border border-red-500/40 shadow-[0_0_15px_rgba(239,68,68,0.2)]"
                : "text-slate-400 hover:text-slate-200 hover:bg-[#181b24] border border-transparent"
            }`}
          >
            <Mail className="w-4 h-4" />
            EMAIL / SMS LURE DECONSTRUCTOR
          </button>
        </div>

        {/* Input Form */}
        <form onSubmit={handleAnalyze} className="space-y-4">
          <div>
            <label className="block text-xs font-mono text-slate-400 mb-2">
              {activeTab === "URL"
                ? "TARGET URL / SUSPICIOUS DOMAIN"
                : "RAW MESSAGE / EMAIL TEXT CONTENT"}
            </label>
            {activeTab === "URL" ? (
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="https://secure-login.suspicious-domain.live/auth or apple[.]com"
                className="w-full px-4 py-3.5 rounded-xl bg-[#0a0b0e] border border-[#262b37] focus:border-red-500 focus:outline-none focus:ring-1 focus:ring-red-500 text-sm font-mono text-slate-200 placeholder-slate-600 transition-all"
              />
            ) : (
              <div className="space-y-3">
                <textarea
                  rows={4}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Paste suspicious email text, SMS message, or payment ultimatum..."
                  className="w-full px-4 py-3 rounded-xl bg-[#0a0b0e] border border-[#262b37] focus:border-red-500 focus:outline-none focus:ring-1 focus:ring-red-500 text-sm font-mono text-slate-200 placeholder-slate-600 transition-all resize-none"
                />
                <input
                  type="text"
                  value={senderMetadata}
                  onChange={(e) => setSenderMetadata(e.target.value)}
                  placeholder="Optional Sender Metadata (e.g. +1-800-ALERT, no-reply@service-update.xyz)"
                  className="w-full px-4 py-2.5 rounded-xl bg-[#0a0b0e] border border-[#262b37] focus:border-red-500 focus:outline-none text-xs font-mono text-slate-300 placeholder-slate-600"
                />
              </div>
            )}
          </div>

          {/* Quick Preset Buttons */}
          <div className="flex flex-wrap items-center gap-2 pt-1">
            <span className="text-[11px] font-mono text-slate-500">EXAMPLES:</span>
            {sampleTargets[activeTab].map((sample, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setInputValue(sample.val)}
                className="text-[11px] font-mono px-2.5 py-1 rounded-md bg-[#181b24] hover:bg-[#202532] text-slate-300 border border-[#2a3040] transition-colors"
              >
                {sample.label}
              </button>
            ))}
          </div>

          {/* Error Banner */}
          {error && (
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-mono flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Submit Action */}
          <div className="pt-2 flex justify-end">
            <button
              type="submit"
              disabled={loading || !inputValue.trim()}
              className="inline-flex items-center gap-2.5 px-6 py-3 rounded-xl bg-red-600 hover:bg-red-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-mono text-xs font-bold tracking-wider transition-all shadow-[0_0_25px_rgba(239,68,68,0.35)]"
            >
              {loading ? (
                <>
                  <Cpu className="w-4 h-4 animate-spin" />
                  ANALYZING TELEMETRY...
                </>
              ) : (
                <>
                  <span>EXECUTE HEURISTIC SCAN</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Investigation Dossier Results View */}
      {report && (
        <div className="rounded-2xl bg-[#12141a] border border-[#222733] p-6 sm:p-8 space-y-6 animate-fade-in shadow-2xl">
          {/* Executive Verdict Banner */}
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-[#1e222d] pb-6">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-slate-500 uppercase">
                  INVESTIGATION DOSSIER:
                </span>
                <span className="text-xs font-mono text-slate-300">{report.scan_id}</span>
              </div>
              <h2 className="text-2xl font-bold text-white tracking-tight">
                {report.target_type} Threat Assessment
              </h2>
              <div className="text-xs font-mono text-slate-400 truncate max-w-2xl">
                TARGET: {report.defanged_target}
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div
                className={`px-4 py-2 rounded-xl text-center border font-mono font-bold ${
                  getRiskColor(report.risk_score).bg
                } ${getRiskColor(report.risk_score).text} ${
                  getRiskColor(report.risk_score).border
                } ${getRiskColor(report.risk_score).glow}`}
              >
                <div className="text-2xl">{report.risk_score}/100</div>
                <div className="text-[10px] tracking-wider">{report.risk_level}</div>
              </div>
            </div>
          </div>

          {/* Executive Layman Verdict Callout */}
          <div
            className={`p-4 rounded-xl border ${
              report.risk_score >= 70
                ? "bg-red-500/10 border-red-500/30 text-red-300"
                : report.risk_score <= 25
                ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                : "bg-yellow-500/10 border-yellow-500/30 text-yellow-300"
            }`}
          >
            <div className="font-mono text-xs font-bold tracking-wider mb-1 uppercase">
              EXECUTIVE VERDICT FOR IMMEDIATE DEFENSE:
            </div>
            <div className="text-sm font-semibold">{report.layman_verdict}</div>
          </div>

          {/* AI Executive Summary */}
          <div className="space-y-2">
            <h3 className="text-xs font-mono text-slate-400 uppercase tracking-wider">
              ANALYST SUMMARY & HEURISTIC FINDINGS
            </h3>
            <p className="text-sm text-slate-300 leading-relaxed bg-[#0d0f14] p-4 rounded-xl border border-[#1e222d]">
              {report.executive_summary}
            </p>
          </div>

          {/* Evidence Items Breakdown */}
          <div className="space-y-3">
            <h3 className="text-xs font-mono text-slate-400 uppercase tracking-wider">
              FORENSIC EVIDENCE & TELEMETRY PROOF ({report.evidence_items.length})
            </h3>
            <div className="space-y-2">
              {report.evidence_items.map((ev, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-xl bg-[#0e1017] border border-[#1e222d] space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-200">{ev.title}</span>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                        ev.severity === "CRITICAL" || ev.severity === "HIGH"
                          ? "bg-red-500/10 text-red-400 border-red-500/30"
                          : ev.severity === "MEDIUM"
                          ? "bg-yellow-500/10 text-yellow-400 border-yellow-500/30"
                          : "bg-blue-500/10 text-blue-400 border-blue-500/30"
                      }`}
                    >
                      {ev.severity} // {ev.category}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">{ev.description}</p>
                  <div className="text-[11px] font-mono text-slate-500 bg-[#07080b] p-2 rounded border border-[#171a24]">
                    PROOF: {ev.technical_proof}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
