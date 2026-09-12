import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  ShieldAlert,
  Search,
  LayoutDashboard,
  History,
  FileText,
  Settings,
  ShieldCheck,
  Menu,
  X,
  Radio,
} from "lucide-react";

interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { label: "Analyze", href: "/analyze", icon: Search },
    { label: "History", href: "/history", icon: History },
    { label: "Reports", href: "/reports", icon: FileText },
    { label: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-[#0a0b0e] text-slate-100 flex flex-col font-sans selection:bg-red-500 selection:text-white">
      {/* Top Cyber Navigation Bar */}
      <header className="sticky top-0 z-50 border-b border-[#1e222d] bg-[#0d0f14]/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Logo & Platform Name */}
          <div className="flex items-center gap-3">
            <Link to="/dashboard" className="flex items-center gap-2.5 group">
              <div className="relative w-9 h-9 rounded-lg bg-gradient-to-br from-red-600 to-red-950 p-0.5 shadow-[0_0_20px_rgba(239,68,68,0.4)] transition-transform group-hover:scale-105">
                <div className="w-full h-full bg-[#0a0b0e] rounded-[7px] flex items-center justify-center border border-red-500/40">
                  <ShieldAlert className="w-5 h-5 text-red-500" />
                </div>
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-1.5">
                  <span className="font-extrabold text-lg tracking-wider text-white">
                    XE<span className="text-red-500">R</span>OX
                  </span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-500/10 text-red-400 font-mono font-semibold border border-red-500/20">
                    CORE 1.0
                  </span>
                </div>
                <span className="text-[10px] tracking-wider text-slate-400 font-mono -mt-1 hidden sm:inline">
                  AI DEFENSIVE INTELLIGENCE
                </span>
              </div>
            </Link>
          </div>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive =
                location.pathname === item.href ||
                (item.href === "/dashboard" && location.pathname === "/");
              return (
                <Link
                  key={item.href}
                  to={item.href}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-mono tracking-wide transition-all ${
                    isActive
                      ? "bg-red-500/10 text-red-400 border border-red-500/30 shadow-[0_0_15px_rgba(239,68,68,0.15)]"
                      : "text-slate-400 hover:text-slate-200 hover:bg-[#151821] border border-transparent"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          {/* System Telemetry Beacon & Auth Status */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-[#12141a] border border-[#262b37] text-xs font-mono text-slate-400">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
              </span>
              <span className="text-emerald-400 font-semibold">GUARD ACTIVE</span>
            </div>

            <Link
              to="/analyze"
              className="hidden lg:flex items-center gap-2 px-4 py-2 rounded-lg bg-red-600 hover:bg-red-500 text-white text-xs font-mono font-semibold tracking-wider transition-all shadow-[0_0_20px_rgba(239,68,68,0.35)]"
            >
              <Radio className="w-3.5 h-3.5 animate-pulse" />
              INSPECT TARGET
            </Link>

            {/* Mobile menu toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg bg-[#151821] border border-[#262b37] text-slate-400 hover:text-white"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile menu drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-[#1e222d] bg-[#0d0f14] px-4 py-3 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.href}
                  to={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-mono ${
                    isActive
                      ? "bg-red-500/15 text-red-400 border border-red-500/30"
                      : "text-slate-300 hover:bg-[#151821]"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </Link>
              );
            })}
          </div>
        )}
      </header>

      {/* Main Content Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Cyber Footer */}
      <footer className="border-t border-[#1e222d] bg-[#0d0f14] py-6 text-xs text-slate-500 font-mono">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-slate-400" />
            <span>XEROX DEFENSIVE CYBERSECURITY ARCHITECTURE // PHASE 1</span>
          </div>
          <div className="text-slate-500">
            WEAPONLESS, PURPOSE DRIVEN. A SAFER DIGITAL TOMORROW.
          </div>
        </div>
      </footer>
    </div>
  );
};
