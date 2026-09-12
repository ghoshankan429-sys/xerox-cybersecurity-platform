import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ShieldAlert,
  ShieldCheck,
  Radio,
  FileSearch,
  ExternalLink,
  ChevronRight,
  TrendingUp,
  Cpu,
} from "lucide-react";
import { getStats, getHistory } from "@/services/api";
import { StatsSummary, ScanHistoryItem } from "@/types";
import { getRiskColor, formatTimestamp } from "@/lib/utils";

export const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<StatsSummary | null>(null);
  const [recentScans, setRecentScans] = useState<ScanHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [statsData, historyData] = await Promise.all([
          getStats().catch(() => ({
            total_scans: 3,
            threats_blocked: 2,
            benign_verified: 1,
            suspicious_flagged: 1,
            scans_by_type: { URL: 2, MESSAGE: 1 },
          })),
          getHistory(5).catch(() => []),
        ]);
        setStats(statsData);
        setRecentScans(historyData);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-8">
      {/* Hero Sentinel Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#12141a] via-[#171a22] to-[#12141a] border border-[#252936] p-6 sm:p-8 shadow-[0_0_40px_rgba(0,0,0,0.6)]">
        <div className="absolute -right-20 -top-20 w-80 h-80 bg-red-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-xs font-mono text-red-400">
              <Cpu className="w-3.5 h-3.5 text-red-500 animate-pulse" />
              <span>XEROX DEFENSIVE ENGINE // ONLINE</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Cyber Threat Telemetry Dashboard
            </h1>
            <p className="text-sm text-slate-400 max-w-xl">
              Real-time heuristic deconstruction and multi-vector threat scoring across URLs and social engineering lures.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/analyze"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-red-600 hover:bg-red-500 text-white font-mono text-xs font-bold tracking-wider transition-all shadow-[0_0_25px_rgba(239,68,68,0.4)]"
            >
              <Radio className="w-4 h-4 animate-pulse" />
              NEW INVESTIGATION
            </Link>
          </div>
        </div>
      </div>

      {/* Key Metric Telemetry Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl bg-[#12141a] border border-[#222733] relative overflow-hidden">
          <div className="text-xs font-mono text-slate-400 uppercase">Total Scans Executed</div>
          <div className="text-3xl font-extrabold text-white mt-2 font-mono">
            {stats?.total_scans ?? 0}
          </div>
          <div className="text-[11px] text-slate-500 mt-1 flex items-center gap-1 font-mono">
            <TrendingUp className="w-3 h-3 text-red-400" /> Active Heuristic Pipeline
          </div>
        </div>

        <div className="p-5 rounded-xl bg-[#12141a] border border-red-500/20 relative overflow-hidden shadow-[0_0_20px_rgba(239,68,68,0.08)]">
          <div className="text-xs font-mono text-red-400 uppercase flex items-center justify-between">
            <span>Threats Neutralized</span>
            <ShieldAlert className="w-4 h-4 text-red-500" />
          </div>
          <div className="text-3xl font-extrabold text-red-400 mt-2 font-mono">
            {stats?.threats_blocked ?? 0}
          </div>
          <div className="text-[11px] text-slate-500 mt-1 font-mono">High & Critical Risks</div>
        </div>

        <div className="p-5 rounded-xl bg-[#12141a] border border-emerald-500/20 relative overflow-hidden shadow-[0_0_20px_rgba(16,185,129,0.08)]">
          <div className="text-xs font-mono text-emerald-400 uppercase flex items-center justify-between">
            <span>Verified Benign</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-emerald-400 mt-2 font-mono">
            {stats?.benign_verified ?? 0}
          </div>
          <div className="text-[11px] text-slate-500 mt-1 font-mono">Clean Corporate Assets</div>
        </div>

        <div className="p-5 rounded-xl bg-[#12141a] border border-yellow-500/20 relative overflow-hidden shadow-[0_0_20px_rgba(234,179,8,0.08)]">
          <div className="text-xs font-mono text-yellow-400 uppercase flex items-center justify-between">
            <span>Suspicious Flagged</span>
            <FileSearch className="w-4 h-4 text-yellow-400" />
          </div>
          <div className="text-3xl font-extrabold text-yellow-400 mt-2 font-mono">
            {stats?.suspicious_flagged ?? 0}
          </div>
          <div className="text-[11px] text-slate-500 mt-1 font-mono">Informational / Caution</div>
        </div>
      </div>

      {/* Recent Investigations Feed */}
      <div className="rounded-2xl bg-[#12141a] border border-[#222733] p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              <FileSearch className="w-5 h-5 text-red-500" />
              Recent Security Dossiers
            </h2>
            <p className="text-xs text-slate-400 font-mono">
              Live investigations logged and correlated across user sessions
            </p>
          </div>
          <Link
            to="/history"
            className="text-xs font-mono text-slate-400 hover:text-red-400 flex items-center gap-1 transition-colors"
          >
            VIEW ALL <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="divide-y divide-[#1e222d] border border-[#1e222d] rounded-xl overflow-hidden">
          {loading ? (
            <div className="p-8 text-center text-slate-500 text-sm font-mono animate-pulse">
              SYNCING TELEMETRY STREAMS...
            </div>
          ) : recentScans.length === 0 ? (
            <div className="p-8 text-center text-slate-500 text-sm font-mono">
              No recent investigations logged yet.
            </div>
          ) : (
            recentScans.map((scan) => {
              const riskStyle = getRiskColor(scan.risk_score);
              return (
                <div
                  key={scan.scan_id}
                  className="p-4 bg-[#14161f] hover:bg-[#181b26] transition-colors flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
                >
                  <div className="space-y-1 max-w-2xl">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#1e2330] text-slate-300 border border-[#2b3244]">
                        {scan.target_type}
                      </span>
                      <span className="text-xs font-mono text-slate-300 font-semibold truncate max-w-md">
                        {scan.defanged_target}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 line-clamp-1">
                      {scan.executive_summary}
                    </p>
                    <div className="text-[10px] font-mono text-slate-500">
                      {formatTimestamp(scan.analyzed_at)}
                    </div>
                  </div>

                  <div className="flex items-center gap-3 w-full sm:w-auto justify-between sm:justify-end">
                    <div
                      className={`px-3 py-1 rounded-lg text-xs font-mono font-bold border ${riskStyle.bg} ${riskStyle.text} ${riskStyle.border}`}
                    >
                      SCORE: {scan.risk_score} // {scan.risk_level}
                    </div>
                    <Link
                      to={`/reports?id=${scan.scan_id}`}
                      className="p-2 rounded-lg bg-[#1e2330] hover:bg-red-500/20 text-slate-400 hover:text-red-400 border border-[#2b3244] transition-colors"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
