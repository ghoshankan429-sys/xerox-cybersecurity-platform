import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { ShieldAlert, Lock, Mail, ArrowRight, AlertTriangle, ShieldCheck } from "lucide-react";
import { useAuth } from "@/features/auth/AuthContext";
import { Input, Button, Card } from "@/components/ui";

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
      setError(err.message || "Invalid analyst credentials. Please verify and retry.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[75vh] flex items-center justify-center px-4">
      <Card className="w-full max-w-md shadow-2xl space-y-6">
        {/* Brand Icon & Heading */}
        <div className="text-center space-y-2">
          <div className="inline-flex p-3 rounded-2xl bg-red-600/10 border border-red-500/20 shadow-red-glow">
            <ShieldAlert className="w-8 h-8 text-xerox-red" />
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Authenticate to XEROX
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Enter analyst credentials to access protected defensive telemetry
          </p>
        </div>

        {error && (
          <div
            role="alert"
            className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-mono flex items-center gap-2.5"
          >
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <Input
            label="OPERATIONAL EMAIL"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
            placeholder="analyst@domain.gov"
            leftIcon={<Mail className="w-4 h-4" />}
          />

          <Input
            label="SECURITY KEY / PASSWORD"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
            placeholder="••••••••••••"
            leftIcon={<Lock className="w-4 h-4" />}
          />

          <Button
            type="submit"
            variant="primary"
            fullWidth
            loading={loading}
            loadingText="AUTHENTICATING..."
            rightIcon={<ArrowRight className="w-4 h-4" />}
          >
            INITIALIZE SESSION
          </Button>
        </form>

        <div className="pt-2 border-t border-xerox-border-subtle flex flex-col sm:flex-row items-center justify-between text-xs font-mono text-slate-400 gap-2">
          <Link
            to="/register"
            className="text-slate-400 hover:text-slate-200 transition-colors"
          >
            Register new analyst account
          </Link>
          <span className="text-[11px] text-slate-500 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            HTTPONLY COOKIE ENCLAVE
          </span>
        </div>
      </Card>
    </div>
  );
};
