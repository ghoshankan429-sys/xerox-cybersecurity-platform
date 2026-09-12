"use client";

import React from "react";
import { SentinelState, RiskLevel } from "@/types/threat";
import { AlertTriangle, CheckCircle2, Activity, Cpu } from "lucide-react";

interface SentinelRobotHUDProps {
  state: SentinelState;
  riskLevel?: RiskLevel;
  riskScore?: number;
  targetPreview?: string;
}

export const SentinelRobotHUD: React.FC<SentinelRobotHUDProps> = ({
  state,
  riskLevel,
  riskScore,
  targetPreview,
}) => {
  // Determine color accents based on current sentinel state
  const isAlert = state === "ALERT" || riskLevel === "CRITICAL" || riskLevel === "HIGH RISK";
  const isVerified = state === "VERIFIED" || riskLevel === "BENIGN";
  const isScanning = state === "SCANNING" || state === "INGESTING" || state === "CORRELATING";

  let glowColor = "rgba(59, 130, 246, 0.4)"; // Default cobalt
  let accentBorder = "border-brand-primary/40";
  let statusText = "SENTINEL ARMED // STANDBY";
  let statusBadgeColor = "bg-blue-500/10 text-blue-400 border-blue-500/30";

  if (isAlert) {
    glowColor = "rgba(239, 68, 68, 0.5)";
    accentBorder = "border-red-500/60 shadow-[0_0_30px_rgba(239,68,68,0.2)]";
    statusText = "THREAT LOCKED // HOSTILE DETECTED";
    statusBadgeColor = "bg-red-500/20 text-red-400 border-red-500/40";
  } else if (isVerified) {
    glowColor = "rgba(16, 185, 129, 0.4)";
    accentBorder = "border-emerald-500/50 shadow-[0_0_25px_rgba(16,185,129,0.15)]";
    statusText = "PERIMETER SECURE // BENIGN";
    statusBadgeColor = "bg-emerald-500/20 text-emerald-400 border-emerald-500/40";
  } else if (isScanning) {
    glowColor = "rgba(6, 182, 212, 0.45)";
    accentBorder = "border-cyan-500/50 shadow-[0_0_30px_rgba(6,182,212,0.2)]";
    statusText = "DEEP SCAN // HEURISTIC DECONSTRUCTION";
    statusBadgeColor = "bg-cyan-500/20 text-cyan-400 border-cyan-500/40";
  }

  return (
    <div
      className={`relative overflow-hidden rounded-2xl bg-surface/90 border ${accentBorder} backdrop-blur-xl p-6 transition-all duration-500`}
      style={{
        boxShadow: `0 0 35px ${glowColor}`,
      }}
    >
      {/* Background Grid Pattern & Radar Sweeper */}
      <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px] opacity-40 pointer-events-none" />
      {isScanning && (
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyan-500/10 to-transparent animate-scan pointer-events-none" />
      )}

      <div className="relative z-10 flex flex-col md:flex-row items-center gap-6">
        {/* Robot Sentinel Head Visual Representation */}
        <div className="relative w-36 h-36 flex-shrink-0 flex items-center justify-center">
          {/* Outer Ambient Rings */}
          <div
            className={`absolute inset-0 rounded-full border border-dashed border-white/20 ${
              isScanning ? "animate-[spin_6s_linear_infinite]" : ""
            }`}
          />
          <div
            className={`absolute inset-2 rounded-full border border-white/10 ${
              isScanning ? "animate-[spin_10s_linear_infinite_reverse]" : ""
            }`}
          />

          {/* SVG Sentinel Head Geometry */}
          <svg
            viewBox="0 0 120 120"
            className="w-28 h-28 drop-shadow-[0_0_15px_rgba(59,130,246,0.5)]"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            {/* Chassis Helmet Base */}
            <path
              d="M30 35 L60 20 L90 35 L98 65 L88 95 L60 105 L32 95 L22 65 Z"
              fill="#0F172A"
              stroke="#334155"
              strokeWidth="2.5"
            />
            {/* Titanium Crown Plate */}
            <path
              d="M40 28 L60 18 L80 28 L75 42 L45 42 Z"
              fill="#1E293B"
              stroke="#475569"
              strokeWidth="1.5"
            />
            {/* Temple Audio/Telemetry Sensors */}
            <rect x="18" y="55" width="6" height="20" rx="2" fill="#3B82F6" opacity="0.8" />
            <rect x="96" y="55" width="6" height="20" rx="2" fill="#3B82F6" opacity="0.8" />

            {/* Glowing Visor Screen */}
            <path
              d="M32 50 Q60 46 88 50 L84 66 Q60 62 36 66 Z"
              fill={isAlert ? "#EF4444" : isVerified ? "#10B981" : "#06B6D4"}
              className={isScanning ? "animate-pulse" : ""}
              opacity="0.9"
            />

            {/* Optical Visor Beam Line */}
            <line
              x1="36"
              y1="58"
              x2="84"
              y2="58"
              stroke="#FFFFFF"
              strokeWidth="1.5"
              strokeDasharray={isScanning ? "4 2" : "none"}
            />

            {/* Core Sternum Power Node */}
            <circle
              cx="60"
              cy="85"
              r="7"
              fill={isAlert ? "#DC2626" : isVerified ? "#059669" : "#2563EB"}
              className="animate-pulse"
            />
            <circle cx="60" cy="85" r="3" fill="#FFFFFF" />

            {/* Cyber Chin Exhaust Slits */}
            <line x1="52" y1="95" x2="68" y2="95" stroke="#475569" strokeWidth="1.5" />
            <line x1="55" y1="99" x2="65" y2="99" stroke="#475569" strokeWidth="1.5" />
          </svg>
        </div>

        {/* Sentinel Live Diagnostic Telemetry */}
        <div className="flex-1 w-full space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2.5 w-2.5">
                <span
                  className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                    isAlert ? "bg-red-400" : isVerified ? "bg-emerald-400" : "bg-cyan-400"
                  }`}
                />
                <span
                  className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
                    isAlert ? "bg-red-500" : isVerified ? "bg-emerald-500" : "bg-cyan-500"
                  }`}
                />
              </span>
              <span className="text-xs font-mono tracking-widest text-slate-400 uppercase">
                XEROX CO-PILOT SENTINEL
              </span>
            </div>

            <div className={`px-2.5 py-1 rounded-md text-xs font-mono border ${statusBadgeColor}`}>
              {riskScore !== undefined ? `SCORE ${riskScore} // ` : ""}{statusText}
            </div>
          </div>

          <div>
            <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
              {isAlert && <AlertTriangle className="w-5 h-5 text-red-400 inline" />}
              {isVerified && <CheckCircle2 className="w-5 h-5 text-emerald-400 inline" />}
              {isScanning && <Activity className="w-5 h-5 text-cyan-400 inline animate-spin" />}
              {!isAlert && !isVerified && !isScanning && (
                <Cpu className="w-5 h-5 text-blue-400 inline" />
              )}
              {isAlert
                ? "Hostile Threat Containment Protocol"
                : isVerified
                ? "Target Integrity Verified"
                : isScanning
                ? "Executing Multi-Vector Analysis..."
                : "Autonomous Security Co-Pilot Ready"}
            </h2>
            <p className="text-sm text-slate-400 mt-1">
              {isAlert
                ? "High-severity adversarial vectors identified. Automated mitigation checklist engaged."
                : isVerified
                ? "Cryptographic TLS records and infrastructure telemetry align with clean corporate operations."
                : isScanning
                ? "Deconstructing DNS records, redirect cascades, TLS certificates, and NLP urgency cues."
                : "Paste any suspicious URL, SMS text, email header, or screenshot to commence real-time inspection."}
            </p>
          </div>

          {targetPreview && (
            <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800 flex items-center gap-2 text-xs font-mono text-slate-300 overflow-hidden text-ellipsis whitespace-nowrap">
              <span className="text-slate-500 flex-shrink-0">INSPECTING:</span>
              <span className="truncate text-blue-300">{targetPreview}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
