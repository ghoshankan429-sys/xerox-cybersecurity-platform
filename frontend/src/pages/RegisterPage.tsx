import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShieldCheck, Lock, Mail, ArrowRight, AlertTriangle } from "lucide-react";
import { useAuth } from "@/features/auth/AuthContext";

export const RegisterPage: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Passwords do not match. Please verify.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    setLoading(true);
    try {
      await register(email.trim(), password);
      navigate("/dashboard", { replace: true });
    } catch (err: any) {
      setError(err.message || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[75vh] flex items-center justify-center px-4">
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

        {error && (
          <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-mono flex items-center gap-2.5">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

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
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#0a0b0e] border border-[#262b37] focus:border-red-500 focus:outline-none text-xs font-mono text-slate-200 placeholder-slate-600"
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
                placeholder="Min 8 chars, uppercase, number, symbol"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#0a0b0e] border border-[#262b37] focus:border-red-500 focus:outline-none text-xs font-mono text-slate-200 placeholder-slate-600"
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
                placeholder="Re-enter your password"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#0a0b0e] border border-[#262b37] focus:border-red-500 focus:outline-none text-xs font-mono text-slate-200 placeholder-slate-600"
              />
            </div>
          </div>

          <div className="p-3 rounded-lg bg-[#0e1017] border border-[#1e222d] text-[11px] font-mono text-slate-400 space-y-1">
            <div className="text-slate-300 font-semibold">Security Requirements:</div>
            <div>• Minimum 8 characters</div>
            <div>• Uppercase & lowercase letters</div>
            <div>• Numbers and special characters</div>
          </div>

          <button
            type="submit"
            disabled={loading || !email || !password || !confirmPassword}
            className="w-full py-3 rounded-xl bg-red-600 hover:bg-red-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-mono text-xs font-bold tracking-wider transition-all flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(239,68,68,0.35)]"
          >
            <span>{loading ? "CREATING ACCOUNT..." : "REGISTER ANALYST"}</span>
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
