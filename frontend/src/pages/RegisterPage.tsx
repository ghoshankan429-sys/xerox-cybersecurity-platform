import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShieldCheck, Lock, Mail, ArrowRight } from "lucide-react";

export const RegisterPage: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const navigate = useNavigate();

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    // Milestone 3 will hook up registration API
    navigate("/login");
  };

  return (
    <div className="min-h-[75vh] flex items-center justify-center">
      <div className="w-full max-w-md p-8 rounded-2xl bg-[#12141a] border border-[#222733] shadow-2xl space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex p-3 rounded-xl bg-red-600/10 border border-red-500/20 shadow-[0_0_20px_rgba(239,68,68,0.3)]">
            <ShieldCheck className="w-8 h-8 text-red-500" />
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Register Analyst Identity
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Create an isolated tenant account for personal threat telemetry
          </p>
        </div>

        <form onSubmit={handleRegister} className="space-y-4">
          <div>
            <label className="block text-xs font-mono text-slate-400 mb-1.5">
              OPERATIONAL EMAIL
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="analyst@domain.com"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#0a0b0e] border border-[#262b37] focus:border-red-500 focus:outline-none text-xs font-mono text-slate-200"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono text-slate-400 mb-1.5">
              SECURITY KEY / PASSWORD
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#0a0b0e] border border-[#262b37] focus:border-red-500 focus:outline-none text-xs font-mono text-slate-200"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono text-slate-400 mb-1.5">
              CONFIRM PASSWORD
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#0a0b0e] border border-[#262b37] focus:border-red-500 focus:outline-none text-xs font-mono text-slate-200"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-3 rounded-xl bg-red-600 hover:bg-red-500 text-white font-mono text-xs font-bold tracking-wider transition-all flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(239,68,68,0.35)]"
          >
            <span>REGISTER ANALYST</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="text-center text-xs font-mono text-slate-500">
          Already registered?{" "}
          <Link to="/login" className="text-red-400 hover:underline">
            Authenticate here
          </Link>
        </div>
      </div>
    </div>
  );
};
