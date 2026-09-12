import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { ShieldAlert, Lock, Mail, ArrowRight, AlertTriangle } from "lucide-react";
import { useAuth } from "@/features/auth/AuthContext";

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as any)?.from?.pathname || "/dashboard";

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login(email.trim(), password);
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err.message || "Invalid credentials. Please verify and retry.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[75vh] flex items-center justify-center px-4">
      <div className="w-full max-w-md p-8 rounded-2xl bg-[#12141a] border border-[#222733] shadow-2xl space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex p-3 rounded-xl bg-red-600/10 border border-red-500/20 shadow-[0_0_20px_rgba(239,68,68,0.3)]">
            <ShieldAlert className="w-8 h-8 text-red-500" />
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Authenticate to XEROX
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Enter your analyst credentials to access protected security telemetry
          </p>
        </div>

        {error && (
          <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-mono flex items-center gap-2.5">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
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
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#0a0b0e] border border-[#262b37] focus:border-red-500 focus:outline-none text-xs font-mono text-slate-200 placeholder-slate-600 transition-all"
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
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#0a0b0e] border border-[#262b37] focus:border-red-500 focus:outline-none text-xs font-mono text-slate-200 placeholder-slate-600 transition-all"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !email || !password}
            className="w-full py-3 rounded-xl bg-red-600 hover:bg-red-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-mono text-xs font-bold tracking-wider transition-all flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(239,68,68,0.35)]"
          >
            <span>{loading ? "AUTHENTICATING..." : "ACCESS PLATFORM"}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="text-center text-xs font-mono text-slate-500">
          Need an account?{" "}
          <Link to="/register" className="text-red-400 hover:underline">
            Register new analyst
          </Link>
        </div>
      </div>
    </div>
  );
};
