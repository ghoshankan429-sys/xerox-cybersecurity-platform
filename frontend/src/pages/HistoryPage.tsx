import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { History, ExternalLink, RefreshCw } from "lucide-react";
import { getHistory } from "@/services/api";
import { ScanHistoryItem } from "@/types";
import { getRiskColor, formatTimestamp } from "@/lib/utils";

export const HistoryPage: React.FC = () => {
  const [history, setHistory] = useState<ScanHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await getHistory(50);
      setHistory(data);
    } catch {
      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-[#1e222d] pb-6">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
            <History className="w-6 h-6 text-red-500" />
            Security Investigation Archive
          </h1>
          <p className="text-xs text-slate-400 font-mono mt-1">
            Authenticated audit log of past forensic scans and deconstructed indicators
          </p>
        </div>

        <button
          onClick={fetchHistory}
          disabled={loading}
          className="inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-[#151821] hover:bg-[#1a1e2a] text-slate-300 font-mono text-xs border border-[#252a37] transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          REFRESH
        </button>
      </div>

      <div className="rounded-2xl bg-[#12141a] border border-[#222733] overflow-hidden">
        {history.length === 0 && !loading ? (
          <div className="p-12 text-center text-slate-500 text-sm font-mono">
            No investigations recorded in your archive.
          </div>
        ) : (
          <div className="divide-y divide-[#1e222d]">
            {history.map((item) => {
              const riskStyle = getRiskColor(item.risk_score);
              return (
                <div
                  key={item.scan_id}
                  className="p-5 hover:bg-[#151822] transition-colors flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
                >
                  <div className="space-y-1.5 max-w-3xl">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#1b202c] text-slate-300 border border-[#252c3d]">
                        {item.target_type}
                      </span>
                      <span className="text-xs font-mono text-slate-200 font-bold truncate max-w-lg">
                        {item.defanged_target}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 line-clamp-2">
                      {item.executive_summary}
                    </p>
                    <div className="text-[10px] font-mono text-slate-500">
                      ID: {item.scan_id} • {formatTimestamp(item.analyzed_at)}
                    </div>
                  </div>

                  <div className="flex items-center gap-3 w-full sm:w-auto justify-between sm:justify-end">
                    <div
                      className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold border ${riskStyle.bg} ${riskStyle.text} ${riskStyle.border}`}
                    >
                      {item.risk_score}/100 // {item.risk_level}
                    </div>
                    <Link
                      to={`/reports?id=${item.scan_id}`}
                      className="p-2 rounded-lg bg-[#1a1e2a] hover:bg-red-500/20 text-slate-400 hover:text-red-400 border border-[#252c3d] transition-colors"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
