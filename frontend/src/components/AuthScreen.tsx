import { FormEvent, useState } from "react";
import { ApiError } from "../api/client";
import { loginUser, registerUser } from "../api/userApi";
import { useAuth } from "../context/AuthContext";

type AuthMode = "login" | "register";

function ShieldLogo() {
  return (
    <svg viewBox="0 0 64 64" fill="none" aria-hidden="true" className="auth-screen__logo-icon">
      <defs>
        <linearGradient id="shieldGrad" x1="8" y1="4" x2="56" y2="60">
          <stop stopColor="#22d3ee" />
          <stop offset="1" stopColor="#3b82f6" />
        </linearGradient>
      </defs>
      <path
        d="M32 4L8 14v16c0 14.5 10.2 28.1 24 32 13.8-3.9 24-17.5 24-32V14L32 4Z"
        stroke="url(#shieldGrad)"
        strokeWidth="2.5"
        fill="rgba(34,211,238,0.08)"
      />
      <circle cx="32" cy="28" r="10" stroke="url(#shieldGrad)" strokeWidth="2" />
      <path
        d="M32 18v10M27 23h10"
        stroke="url(#shieldGrad)"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M22 38c3 4 6.5 6 10 6s7-2 10-6"
        stroke="url(#shieldGrad)"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

function MailIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="3" y="5" width="18" height="14" rx="2" stroke="currentColor" strokeWidth="1.75" />
      <path d="M3 7l9 6 9-6" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
    </svg>
  );
}

function LockIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="5" y="11" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="1.75" />
      <path
        d="M8 11V8a4 4 0 118 0v3"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
    </svg>
  );
}

function UserIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="1.75" />
      <path d="M5 20c0-3.5 3-6 7-6s7 2.5 7 6" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
    </svg>
  );
}

const FEATURES = [
  {
    label: "AI Powered Protection",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M12 2l8 3v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V5l8-3z" stroke="currentColor" strokeWidth="1.75" />
      </svg>
    ),
  },
  {
    label: "Real-time Threat Detection",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.75" />
        <path d="M2 12h20M12 2a15 15 0 010 20M12 2a15 15 0 000 20" stroke="currentColor" strokeWidth="1.75" />
      </svg>
    ),
  },
  {
    label: "Secure & Private",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="5" y="11" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="1.75" />
        <path d="M8 11V8a4 4 0 118 0v3" stroke="currentColor" strokeWidth="1.75" />
      </svg>
    ),
  },
  {
    label: "Smart Insights & Reports",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M4 19V5M4 19H20M8 15V11M12 15V7M16 15V9" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
      </svg>
    ),
  },
];

export default function AuthScreen() {
  const { login } = useAuth();
  const [mode, setMode] = useState<AuthMode>("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const user =
        mode === "register"
          ? await registerUser({ name, email, password })
          : await loginUser({ email, password });

      login(user);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else if (err instanceof TypeError) {
        setError(
          "Unable to reach the CyberShield AI backend. Make sure the API server is running on port 8000.",
        );
      } else {
        setError("Authentication failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  function switchMode(nextMode: AuthMode) {
    setMode(nextMode);
    setError(null);
  }

  return (
    <div className="auth-screen">
      <div className="auth-screen__backdrop" aria-hidden="true">
        <div className="auth-screen__grid" />
        <div className="auth-screen__glow auth-screen__glow--left" />
        <div className="auth-screen__glow auth-screen__glow--right" />
        <div className="auth-screen__waves" />
      </div>

      <div className="auth-screen__hero" aria-hidden="true">
        <div className="auth-screen__hero-shield">
          <div className="auth-screen__hero-globe" />
          <div className="auth-screen__hero-lock">
            <LockIcon />
          </div>
        </div>
        <div className="auth-screen__hero-hacker" />
        <div className="auth-screen__hero-scan">
          <span>https://</span>
          <span className="auth-screen__hero-scan-check">✓</span>
        </div>
        <div className="auth-screen__hero-lines" />
      </div>

      <main className="auth-screen__main">
        <div className="auth-screen__card">
          <header className="auth-screen__brand">
            <ShieldLogo />
            <div>
              <h1 className="auth-screen__brand-title">
                CyberShield <span>AI</span>
              </h1>
              <p className="auth-screen__brand-tagline">Smart Protection. Real Security.</p>
            </div>
          </header>

          <div className="auth-screen__divider" />

          <div className="auth-screen__welcome">
            <h2>{mode === "login" ? "Welcome Back!" : "Create Account"}</h2>
            <p>
              {mode === "login"
                ? "Sign in to continue to your secure dashboard"
                : "Register to access your CyberShield AI security dashboard"}
            </p>
          </div>

          <form className="auth-screen__form" onSubmit={handleSubmit} noValidate>
            {mode === "register" && (
              <label className="auth-screen__field">
                <span className="auth-screen__field-icon">
                  <UserIcon />
                </span>
                <input
                  type="text"
                  autoComplete="name"
                  placeholder="Full name"
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  disabled={loading}
                  required
                />
              </label>
            )}

            <label className="auth-screen__field">
              <span className="auth-screen__field-icon">
                <MailIcon />
              </span>
              <input
                type="email"
                autoComplete="email"
                placeholder="Email Address"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                disabled={loading}
                required
              />
            </label>

            <label className="auth-screen__field auth-screen__field--password">
              <span className="auth-screen__field-icon">
                <LockIcon />
              </span>
              <input
                type={showPassword ? "text" : "password"}
                autoComplete={mode === "login" ? "current-password" : "new-password"}
                placeholder="Password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                disabled={loading}
                minLength={8}
                required
              />
              <button
                type="button"
                className="auth-screen__toggle-password"
                onClick={() => setShowPassword((value) => !value)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </label>

            {mode === "login" && (
              <div className="auth-screen__forgot">
                <button type="button" className="auth-screen__link">
                  Forgot Password?
                </button>
              </div>
            )}

            {error && (
              <div className="auth-screen__error" role="alert">
                {error}
              </div>
            )}

            <button className="auth-screen__submit" type="submit" disabled={loading}>
              {loading
                ? "Please wait…"
                : mode === "login"
                  ? "Sign In"
                  : "Create Account"}
            </button>
          </form>

          <div className="auth-screen__switch">
            <span className="auth-screen__switch-line" />
            <span>or</span>
            <span className="auth-screen__switch-line" />
          </div>

          <p className="auth-screen__footer-text">
            {mode === "login" ? "Don't have an account?" : "Already have an account?"}{" "}
            <button
              type="button"
              className="auth-screen__link"
              onClick={() => switchMode(mode === "login" ? "register" : "login")}
            >
              {mode === "login" ? "Create Account" : "Sign In"}
            </button>
          </p>
        </div>

        <footer className="auth-screen__features">
          {FEATURES.map((feature) => (
            <div key={feature.label} className="auth-screen__feature">
              <span className="auth-screen__feature-icon">{feature.icon}</span>
              <span>{feature.label}</span>
            </div>
          ))}
        </footer>
      </main>
    </div>
  );
}
