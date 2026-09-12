import React, { useState } from "react";
import {
  Globe,
  ShieldAlert,
  Search,
  Activity,
  CheckCircle2,
  Radio,
  Zap,
} from "lucide-react";
import { Card, Badge, RiskBadge, Input } from "@/components/ui";

interface ThreatFeedItem {
  indicator: string;
  type: "DOMAIN" | "IP" | "URL" | "HASH";
  threat_actor: string;
  category: string;
  severity: "CRITICAL" | "HIGH RISK" | "SUSPICIOUS";
  confidence: number;
  reported_at: string;
}

const DEMO_FEEDS: ThreatFeedItem[] = [
  {
    indicator: "apple-id-verify[.]support-secure[.]live",
    type: "DOMAIN",
    threat_actor: "UNC-2481 (Financial Phishing Group)",
    category: "Credential Harvesting",
    severity: "CRITICAL",
    confidence: 96,
    reported_at: "10 mins ago",
  },
  {
    indicator: "198.51.100.42",
    type: "IP",
    threat_actor: "Storm-0912",
    category: "C2 / Reverse Proxy",
    severity: "HIGH RISK",
    confidence: 89,
    reported_at: "35 mins ago",
  },
  {
    indicator: "hxxps://usps-redelivery-support[.]xyz/track",
    type: "URL",
    threat_actor: "SmishX Lure Network",
    category: "Postal Smishing",
    severity: "CRITICAL",
    confidence: 94,
    reported_at: "1 hour ago",
  },
  {
    indicator: "m365-renewal[.]club",
    type: "DOMAIN",
    threat_actor: "Generic Phishing Kit",
    category: "Corporate Brand Spoof",
    severity: "SUSPICIOUS",
    confidence: 78,
    reported_at: "3 hours ago",
  },
  {
    indicator: "203.0.113.89",
    type: "IP",
    threat_actor: "Bulletproof Hoster AS8921",
    category: "Malicious Hosting",
    severity: "HIGH RISK",
    confidence: 84,
    reported_at: "5 hours ago",
  },
];

export const ThreatIntelPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState("");

  const filteredFeeds = DEMO_FEEDS.filter(
    (item) =>
      item.indicator.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.threat_actor.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-xerox-border-subtle pb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-mono text-blue-400 mb-2">
            <Radio className="w-3.5 h-3.5 animate-pulse" />
            <span>GLOBAL THREAT RADAR // TELEMETRY FEED</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <Globe className="w-7 h-7 text-blue-400" />
            Threat Intelligence Observatory
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 font-sans mt-1">
            Continuous correlation of malicious indicators, active campaigns, and adversary infrastructure.
          </p>
        </div>

        <Badge variant="safe" size="md" icon={<Activity className="w-3.5 h-3.5 animate-pulse" />}>
          FEEDS SYNCHRONIZED
        </Badge>
      </div>

      {/* Threat Vector Telemetry Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card variant="default">
          <div className="text-xs font-mono text-slate-400 uppercase">Active Campaigns Tracked</div>
          <div className="text-2xl sm:text-3xl font-mono font-extrabold text-white mt-2">1,248</div>
          <div className="text-[11px] font-mono text-emerald-400 mt-1 flex items-center gap-1">
            <Zap className="w-3 h-3" /> Live global heuristics
          </div>
        </Card>

        <Card variant="default">
          <div className="text-xs font-mono text-red-400 uppercase">Phishing Lures Indexed</div>
          <div className="text-2xl sm:text-3xl font-mono font-extrabold text-red-400 mt-2">24,592</div>
          <div className="text-[11px] font-mono text-slate-500 mt-1">Last 24 hours</div>
        </Card>

        <Card variant="default">
          <div className="text-xs font-mono text-amber-400 uppercase">Smishing Gateways</div>
          <div className="text-2xl sm:text-3xl font-mono font-extrabold text-amber-400 mt-2">3,810</div>
          <div className="text-[11px] font-mono text-slate-500 mt-1">Telecom carrier alerts</div>
        </Card>

        <Card variant="default">
          <div className="text-xs font-mono text-blue-400 uppercase">Telemetry Feed Health</div>
          <div className="text-2xl sm:text-3xl font-mono font-extrabold text-blue-400 mt-2">99.98%</div>
          <div className="text-[11px] font-mono text-emerald-400 mt-1 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" /> All providers nominal
          </div>
        </Card>
      </div>

      {/* Intelligence Feed Section */}
      <div className="rounded-2xl bg-xerox-surface border border-xerox-border p-6 shadow-panel space-y-5">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-xerox-red" />
              Real-Time High-Confidence Indicators of Compromise (IOCs)
            </h3>
            <p className="text-xs text-slate-400 font-sans">
              Curated intelligence stream powering automated XEROX heuristic validation.
            </p>
          </div>

          <div className="w-full sm:w-72">
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search IOC, actor, category..."
              leftIcon={<Search className="w-4 h-4" />}
            />
          </div>
        </div>

        {/* Table of Indicators */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-xerox-surface-elevated/70 text-slate-400 uppercase border-y border-xerox-border-subtle">
              <tr>
                <th className="px-4 py-3">Indicator</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Threat Actor / Campaign</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">Severity</th>
                <th className="px-4 py-3">Confidence</th>
                <th className="px-4 py-3">Reported</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-xerox-border-subtle text-slate-200">
              {filteredFeeds.map((feed, idx) => (
                <tr key={idx} className="hover:bg-xerox-surface-elevated/50 transition-colors">
                  <td className="px-4 py-3.5 font-bold text-white">{feed.indicator}</td>
                  <td className="px-4 py-3.5">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] border border-slate-700">
                      {feed.type}
                    </span>
                  </td>
                  <td className="px-4 py-3.5 text-slate-300">{feed.threat_actor}</td>
                  <td className="px-4 py-3.5 text-slate-400">{feed.category}</td>
                  <td className="px-4 py-3.5">
                    <RiskBadge level={feed.severity} size="sm" />
                  </td>
                  <td className="px-4 py-3.5 font-bold text-slate-100">{feed.confidence}%</td>
                  <td className="px-4 py-3.5 text-slate-500">{feed.reported_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
