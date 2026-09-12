import React from "react";
import { Settings, Shield, Database } from "lucide-react";

export const SettingsPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="border-b border-[#1e222d] pb-4">
        <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
          <Settings className="w-6 h-6 text-red-500" />
          Sentinel Platform Configuration
        </h1>
        <p className="text-xs text-slate-400 font-mono mt-1">
          Threat engine parameters, authentication keys, and telemetry settings
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-6 rounded-2xl bg-[#12141a] border border-[#222733] space-y-3">
          <div className="flex items-center gap-2 text-sm font-bold text-white">
            <Shield className="w-4 h-4 text-red-500" />
            Threat Intelligence Integrations
          </div>
          <p className="text-xs text-slate-400 font-mono">
            External reputation feed status:
          </p>
          <div className="space-y-2 pt-2">
            <div className="flex items-center justify-between text-xs font-mono p-2.5 rounded-lg bg-[#181b24] border border-[#252b3a]">
              <span className="text-slate-300">VirusTotal v3 Adapter</span>
              <span className="text-emerald-400">CONFIGURED</span>
            </div>
            <div className="flex items-center justify-between text-xs font-mono p-2.5 rounded-lg bg-[#181b24] border border-[#252b3a]">
              <span className="text-slate-300">Redis Indicator Cache</span>
              <span className="text-emerald-400">ACTIVE (TTL 24H)</span>
            </div>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-[#12141a] border border-[#222733] space-y-3">
          <div className="flex items-center gap-2 text-sm font-bold text-white">
            <Database className="w-4 h-4 text-red-500" />
            Data Isolation & Privacy
          </div>
          <p className="text-xs text-slate-400 font-mono">
            User-scoped tenant isolation is enforced at the database layer.
          </p>
          <div className="pt-2 text-xs font-mono text-slate-500">
            • Retention Period: 30 Days (configurable)<br />
            • Defanged Indicators on export<br />
            • Async Audit Dispatcher Active
          </div>
        </div>
      </div>
    </div>
  );
};
