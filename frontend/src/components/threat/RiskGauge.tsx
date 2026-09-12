"use client";

import React from "react";
import { RiskLevel } from "@/types/threat";

interface RiskGaugeProps {
  score: number;
  level: RiskLevel;
  confidence: number;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({ score, level, confidence }) => {
  // SVG circular arc calculation
  // Radius = 60, Circumference = 2 * PI * 60 ~= 376.99
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  // Normalized offset: 0 -> circumference, 100 -> 0
  const strokeDashoffset = circumference - (score / 100) * circumference;

  let color = "#10B981"; // Emerald
  let badgeBg = "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
  let label = "SAFE / BENIGN";

  if (level === "CRITICAL") {
    color = "#EF4444";
    badgeBg = "bg-red-500/15 text-red-400 border-red-500/40 animate-pulse";
    label = "CRITICAL THREAT";
  } else if (level === "HIGH RISK") {
    color = "#F97316";
    badgeBg = "bg-orange-500/15 text-orange-400 border-orange-500/40";
    label = "HIGH RISK";
  } else if (level === "SUSPICIOUS") {
    color = "#F59E0B";
    badgeBg = "bg-amber-500/15 text-amber-400 border-amber-500/40";
    label = "SUSPICIOUS";
  } else if (level === "LOW RISK") {
    color = "#06B6D4";
    badgeBg = "bg-cyan-500/10 text-cyan-400 border-cyan-500/30";
    label = "LOW RISK";
  }

  return (
    <div className="flex flex-col items-center justify-center p-6 bg-surface rounded-2xl border border-surface-border">
      <div className="relative w-40 h-40 flex items-center justify-center">
        <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 140 140">
          {/* Track background */}
          <circle
            cx="70"
            cy="70"
            r={radius}
            stroke="#1e293b"
            strokeWidth="10"
            fill="transparent"
          />
          {/* Progress Arc */}
          <circle
            cx="70"
            cy="70"
            r={radius}
            stroke={color}
            strokeWidth="10"
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        {/* Center score readout */}
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className="text-4xl font-black text-white tracking-tight font-mono">{score}</span>
          <span className="text-[10px] font-mono text-slate-400 tracking-wider">OUT OF 100</span>
        </div>
      </div>

      {/* Threat Level Badge */}
      <div className={`mt-3 px-3.5 py-1 rounded-full text-xs font-mono font-bold border ${badgeBg}`}>
        {label}
      </div>

      {/* Confidence metric */}
      <div className="mt-2 text-xs font-mono text-slate-400 flex items-center gap-1.5">
        <span>CONFIDENCE:</span>
        <span className="text-slate-200 font-semibold">{Math.round(confidence * 100)}%</span>
      </div>
    </div>
  );
};
