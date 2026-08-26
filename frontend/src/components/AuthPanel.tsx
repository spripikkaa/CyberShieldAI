import { FormEvent, useState } from "react";
import { ApiError } from "../api/client";
import { loginUser, registerUser } from "../api/userApi";
import { useAuth } from "../context/AuthContext";

type AuthMode = "login" | "register";

interface AuthPanelProps {
  onSuccess?: () => void;
}

export default function AuthPanel({ onSuccess }: AuthPanelProps) {
  const { login } = useAuth();
  const [mode, setMode] = useState<AuthMode>("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
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
      onSuccess?.();
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
    <section className="auth-panel">
      <header className="auth-panel__header">
        <p className="auth-panel__eyebrow">Account Access</p>
        <h2 className="auth-panel__title">
          {mode === "login" ? "Welcome back" : "Create your account"}
        </h2>
        <p className="auth-panel__subtitle">
          {mode === "login"
            ? "Sign in to save scan reports and view your history."
            : "Register to persist scans and unlock your security dashboard."}
        </p>
      </header>

      <div className="auth-panel__tabs" role="tablist" aria-label="Authentication mode">
        <button
          type="button"
          role="tab"
          aria-selected={mode === "login"}
          className={`auth-panel__tab${mode === "login" ? " auth-panel__tab--active" : ""}`}
          onClick={() => switchMode("login")}
        >
          Login
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={mode === "register"}
          className={`auth-panel__tab${mode === "register" ? " auth-panel__tab--active" : ""}`}
          onClick={() => switchMode("register")}
        >
          Register
        </button>
      </div>

      <form className="auth-panel__form" onSubmit={handleSubmit} noValidate>
        {mode === "register" && (
          <label className="auth-panel__field">
            <span>Full name</span>
            <input
              type="text"
              autoComplete="name"
              placeholder="Jane Doe"
              value={name}
              onChange={(event) => setName(event.target.value)}
              disabled={loading}
              required
            />
          </label>
        )}

        <label className="auth-panel__field">
          <span>Email address</span>
          <input
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            disabled={loading}
            required
          />
        </label>

        <label className="auth-panel__field">
          <span>Password</span>
          <input
            type="password"
            autoComplete={mode === "login" ? "current-password" : "new-password"}
            placeholder="Minimum 8 characters"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            disabled={loading}
            minLength={8}
            required
          />
        </label>

        {error && (
          <div className="scanner-alert scanner-alert--error" role="alert">
            <strong>Authentication failed.</strong> {error}
          </div>
        )}

        <button className="auth-panel__submit" type="submit" disabled={loading}>
          {loading
            ? "Please wait…"
            : mode === "login"
              ? "Sign in"
              : "Create account"}
        </button>
      </form>
    </section>
  );
}
