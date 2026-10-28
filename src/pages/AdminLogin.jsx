import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { api } from "@/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Shield, Mail, Lock, Eye, EyeOff, Loader2, ArrowRight, ShieldAlert, KeyRound, AlertTriangle } from "lucide-react";
import AuthLayout from "@/components/auth/AuthLayout";

export default function AdminLogin() {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const requiresAdmin = searchParams.get("reason") === "admin_required";

  const [authMode, setAuthMode] = useState("pin"); // "pin" | "password"
  const [email, setEmail] = useState("admin@crbcl.ca");
  const [password, setPassword] = useState("");
  const [pin, setPin] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showPin, setShowPin] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handlePinChange = (e) => {
    const val = e.target.value.replace(/\D/g, "").slice(0, 6);
    setPin(val);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (authMode === "pin") {
      if (pin.length !== 6 || !/^\d{6}$/.test(pin)) {
        setError("Please enter a valid 6-digit administrator PIN.");
        return;
      }
    } else {
      if (!password) {
        setError("Please enter your administrator password.");
        return;
      }
    }

    setLoading(true);
    try {
      let res;
      if (authMode === "pin") {
        res = await api.auth.loginViaPin(email, pin);
      } else {
        res = await api.auth.loginViaEmailPassword(email, password);
      }

      const user = res?.user || (await api.auth.me().catch(() => null));
      const roles = Array.isArray(user?.roles) ? user.roles : (user?.role ? [user.role] : []);
      const isItAdmin = 
        user?.role === "admin" ||
        roles.includes("it_admin") ||
        roles.includes("admin") ||
        user?.email === "admin@crbcl.ca" ||
        email.trim().toLowerCase() === "admin@crbcl.ca";

      if (!isItAdmin) {
        setError("Access Denied: The /admin portal is exclusively for IT Administrators and System Admins. Directors, leadership, and staff please use the standard portal.");
        setLoading(false);
        return;
      }

      window.location.href = "/admin";
    } catch (err) {
      setError(err.message || (authMode === "pin" ? "Invalid 6-digit PIN" : "Invalid administrator credentials"));
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      icon={Shield}
      title="IT Admin Portal"
      subtitle="Restricted sign-in exclusively for CRBCL IT Administrators & System Admins"
      footer={
        <div className="space-y-2 text-center text-xs">
          <p className="text-muted-foreground">
            Director, executive, supervisor, or frontline staff?
          </p>
          <Link to="/login" className="inline-flex items-center text-primary font-medium hover:underline">
            Go to Standard Portal <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </Link>
        </div>
      }
    >
      {/* Notice if redirected because user had a staff session */}
      {requiresAdmin && (
        <div className="mb-4 p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-left flex items-start gap-2.5 text-xs text-amber-800 dark:text-amber-200">
          <AlertTriangle className="w-4 h-4 mt-0.5 text-amber-600 flex-shrink-0" />
          <div>
            <div className="font-bold">Administrator Authentication Required</div>
            <div className="text-[11px] opacity-90 mt-0.5">
              You are accessing the <strong>IT Admin Portal</strong>. If you are currently logged in as a Supervisor or Caseworker, please sign in with an IT Administrator account below.
            </div>
          </div>
        </div>
      )}

      {/* Mode Switcher Tabs */}
      <div className="grid grid-cols-2 gap-1 p-1 bg-[#F5F2EF] rounded-xl mb-4 border border-[#E8E3DF]">
        <button
          type="button"
          onClick={() => {
            setAuthMode("pin");
            setError("");
          }}
          className={`flex items-center justify-center gap-1.5 py-2 text-xs font-semibold rounded-lg transition ${
            authMode === "pin"
              ? "bg-purple-700 text-white shadow-sm"
              : "text-[#786F6B] hover:text-[#1F1A17]"
          }`}
        >
          <KeyRound className="w-3.5 h-3.5" />
          6-Digit PIN
        </button>
        <button
          type="button"
          onClick={() => {
            setAuthMode("password");
            setError("");
          }}
          className={`flex items-center justify-center gap-1.5 py-2 text-xs font-semibold rounded-lg transition ${
            authMode === "password"
              ? "bg-purple-700 text-white shadow-sm"
              : "text-[#786F6B] hover:text-[#1F1A17]"
          }`}
        >
          <Lock className="w-3.5 h-3.5" />
          Password
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 text-left">
        {error && (
          <div className="p-3 text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-md flex items-start gap-2">
            <ShieldAlert className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="space-y-1.5">
          <Label htmlFor="admin-email" className="text-[#1F1A17]">Administrator Work Email</Label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#786F6B]" />
            <Input
              id="admin-email"
              type="email"
              required
              placeholder="admin@crbcl.ca"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="pl-9 h-11 bg-white border-[#E8E3DF] text-[#1F1A17] placeholder:text-[#9E9590]"
              disabled={loading}
              autoComplete="username"
            />
          </div>
        </div>

        {authMode === "pin" ? (
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <Label htmlFor="admin-pin" className="text-[#1F1A17]">Administrator 6-Digit PIN</Label>
              <button
                type="button"
                onClick={() => {
                  setAuthMode("password");
                  setError("");
                }}
                className="text-xs text-purple-700 hover:underline"
              >
                Use Password
              </button>
            </div>
            <div className="relative">
              <KeyRound className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#786F6B]" />
              <Input
                id="admin-pin"
                type={showPin ? "text" : "password"}
                inputMode="numeric"
                pattern="[0-9]*"
                maxLength={6}
                required
                placeholder="••••••"
                value={pin}
                onChange={handlePinChange}
                className="pl-9 pr-10 h-11 bg-white border-[#E8E3DF] text-[#1F1A17] placeholder:text-[#9E9590] tracking-widest font-mono text-center text-lg"
                disabled={loading}
                autoFocus
              />
              <button
                type="button"
                onClick={() => setShowPin(!showPin)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[#786F6B] hover:text-[#1F1A17]"
              >
                {showPin ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <p className="text-[11px] text-[#786F6B] text-center mt-1">
              Enter your synced 6-digit administrator PIN (default: <span className="font-mono font-medium">123456</span>)
            </p>
          </div>
        ) : (
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <Label htmlFor="admin-password" className="text-[#1F1A17]">Administrator Password</Label>
              <Link to="/forgot-password" className="text-xs text-[#8B2626] hover:underline">
                Forgot password?
              </Link>
            </div>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#786F6B]" />
              <Input
                id="admin-password"
                type={showPassword ? "text" : "password"}
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="pl-9 pr-10 h-11 bg-white border-[#E8E3DF] text-[#1F1A17] placeholder:text-[#9E9590]"
                disabled={loading}
                autoComplete="current-password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[#786F6B] hover:text-[#1F1A17]"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>
        )}

        <Button 
          type="submit" 
          className="w-full h-11 text-sm font-semibold bg-purple-700 hover:bg-purple-800 text-white shadow-sm mt-2" 
          disabled={loading || (authMode === "pin" && pin.length !== 6)}
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
              Verifying...
            </>
          ) : authMode === "pin" ? (
            <>
              <KeyRound className="w-4 h-4 mr-2" />
              Unlock Admin Portal with PIN
            </>
          ) : (
            <>
              <Shield className="w-4 h-4 mr-2" />
              Access Admin Portal
            </>
          )}
        </Button>
      </form>
    </AuthLayout>
  );
}
