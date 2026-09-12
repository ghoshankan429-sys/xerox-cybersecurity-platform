import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { FileText, AlertTriangle } from "lucide-react";
import { getReport } from "@/services/api";
import { ThreatReport } from "@/types";
import { getRiskColor, formatTimestamp } from "@/lib/utils";

export const ReportsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const scanId = searchParams.get("id");
  const [report, setReport] = useState<ThreatReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (scanId) {
      setLoading(true);
      getReport(scanId)
        .then(setReport)
        .catch((err) => setError(err.message || "Could not retrieve report."))
        .finally(() => setLoading(false));
    }
  }, [scanId]);

  if (!scanId) {
    return (
      <div className="max-w-4xl mx-auto text-center py-16 space-y-4">
        <FileText className="w-12 h-12 text-slate-600 mx-auto" />
        <h2 className="text-xl font-bold text-white">No Security Report Selected</h2>
        <p className="text-sm text-slate-400 font-mono">
          Select an investigation from the dashboard or history archive to view its complete telemetry dossier.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto text-center py-16 text-slate-400 font-mono text-sm animate-pulse">
        RETRIEVING ENCRYPTED SECURITY DOSSIER...
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-4xl mx-auto p-6 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-400 font-mono text-xs flex items-center gap-3">
        <AlertTriangle className="w-5 h-5 flex-shrink-0" />
        <span>{error || "Report could not be found."}</span>
      </div>
    );
  }

  const riskStyle = getRiskColor(report.risk_score);

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between border-b border-[#1e222d] pb-4">
        <div className="space-y-1">
          <span className="text-[11px] font-mono text-slate-500 uppercase">
            DOSSIER ID: {report.scan_id} • {formatTimestamp(report.analyzed_at)}
          </span>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Security Intelligence Report
          </h1>
        </div>
        <div
          className={`px-4 py-2 rounded-xl text-center border font-mono font-bold ${riskStyle.bg} ${riskStyle.text} ${riskStyle.border}`}
        >
          {report.risk_score}/100 // {report.risk_level}
        </div>
      </div>

      <div className="p-6 rounded-2xl bg-[#12141a] border border-[#222733] space-y-4">
        <div className="text-xs font-mono text-slate-400 uppercase">Executive Layman Verdict</div>
        <div className="p-4 rounded-xl bg-[#181b24] border border-[#282f3f] text-sm text-slate-200">
          {report.layman_verdict}
        </div>

        <div className="text-xs font-mono text-slate-400 uppercase pt-2">Analyst Summary</div>
        <p className="text-xs text-slate-300 leading-relaxed bg-[#0e1017] p-4 rounded-xl border border-[#1e222d]">
          {report.executive_summary}
        </p>

        <div className="text-xs font-mono text-slate-400 uppercase pt-2">
          Forensic Evidence ({report.evidence_items.length})
        </div>
        <div className="space-y-2">
          {report.evidence_items.map((ev, i) => (
            <div key={i} className="p-4 rounded-xl bg-[#0e1017] border border-[#1e222d] space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-200">{ev.title}</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/30">
                  {ev.severity}
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
  );
};
