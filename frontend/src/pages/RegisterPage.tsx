import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShieldCheck, Lock, Mail, ArrowRight, AlertTriangle } from "lucide-react";
import { useAuth } from "@/features/auth/AuthContext";
import { Input, Button, Card } from "@/components/ui";

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
      <Card className="w-full max-w-md shadow-2xl space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex p-3 rounded-2xl bg-red-600/10 border border-red-500/20 shadow-red-glow">
            <ShieldCheck className="w-8 h-8 text-xerox-red" />
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Register Analyst Identity
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Create an isolated tenant account for authenticated threat telemetry
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

        <form onSubmit={handleRegister} className="space-y-4">
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
            autoComplete="new-password"
            placeholder="Minimum 8 characters"
            leftIcon={<Lock className="w-4 h-4" />}
            helperText="Requires at least 8 characters, 1 number, and 1 uppercase or special character."
          />

          <Input
            label="CONFIRM PASSWORD"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            autoComplete="new-password"
            placeholder="Repeat password"
            leftIcon={<Lock className="w-4 h-4" />}
          />

          <Button
            type="submit"
            variant="primary"
            fullWidth
            loading={loading}
            loadingText="PROVISIONING ACCOUNT..."
            rightIcon={<ArrowRight className="w-4 h-4" />}
          >
            CREATE OPERATIONAL ACCOUNT
          </Button>
        </form>

        <div className="pt-2 border-t border-xerox-border-subtle text-center text-xs font-mono text-slate-400">
          Already registered?{" "}
          <Link
            to="/login"
            className="text-red-400 hover:text-red-300 transition-colors font-semibold"
          >
            Authenticate here
          </Link>
        </div>
      </Card>
    </div>
  );
};
