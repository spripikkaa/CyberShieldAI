import { FormEvent, useState } from "react";
import { ApiError, predictUrl } from "../api/predictApi";
import { useAuth } from "../context/AuthContext";
import type { ScanResult } from "../types/scan";
import { getSecurityRecommendation } from "../utils/recommendations";
import LoadingState from "./LoadingState";
import ScanResultCard from "./ScanResultCard";
import ScannerHeader from "./ScannerHeader";

interface UrlScannerProps {
  onScanComplete?: (result: ScanResult) => void;
  onAskAi?: (result: ScanResult) => void;
}

function normalizeUrlInput(value: string): string {
  const trimmed = value.trim();
  if (!trimmed) return trimmed;
  if (/^https?:\/\//i.test(trimmed)) return trimmed;
  return `https://${trimmed}`;
}

function isValidUrl(value: string): boolean {
  try {
    const parsed = new URL(value);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

export default function UrlScanner({
  onScanComplete,
  onAskAi,
}: UrlScannerProps) {
  const { userId, user } = useAuth();
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ScanResult | null>(null);

  async function handleScan(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setResult(null);

    const normalizedUrl = normalizeUrlInput(url);
    if (!normalizedUrl) {
      setError("Please enter a URL to scan.");
      return;
    }

    if (!isValidUrl(normalizedUrl)) {
      setError("Enter a valid website URL (for example, https://example.com).");
      return;
    }

    setLoading(true);

    try {
      const response = await predictUrl(normalizedUrl, userId ?? undefined);
      const status = response.prediction === "Phishing" ? "phishing" : "safe";

      const recommendation = getSecurityRecommendation(
        response.prediction,
        response.confidence,
      );

      const scanResult: ScanResult = {
        url: normalizedUrl,
        status,
        prediction: response.prediction,
        confidence: response.confidence,
        recommendation,
      };

      setResult(scanResult);
      onScanComplete?.(scanResult);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else if (err instanceof TypeError) {
        setError(
          "Unable to reach the CyberShield AI backend. Make sure the API server is running on port 8000.",
        );
      } else {
        setError("Something went wrong while scanning. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="scanner">
      <div className="scanner__panel">
        <ScannerHeader />

        {user && (
          <div className="scanner-auth-banner" role="status">
            Signed in as <strong>{user.name}</strong>. Scans are saved to your history.
          </div>
        )}

        <form className="scanner-form" onSubmit={handleScan} noValidate>
          <label className="scanner-form__label" htmlFor="url-input">
            Website URL
          </label>
          <div className="scanner-form__row">
            <div className="scanner-form__input-wrap">
              <svg
                className="scanner-form__input-icon"
                viewBox="0 0 24 24"
                fill="none"
                aria-hidden="true"
              >
                <path
                  d="M10 13a5 5 0 0 1 7.07 0l1.41 1.41a5 5 0 0 1-7.07 7.07l-.88-.88"
                  stroke="currentColor"
                  strokeWidth="1.75"
                  strokeLinecap="round"
                />
                <path
                  d="M14 11a5 5 0 0 1-7.07 0L5.52 9.59a5 5 0 0 1 7.07-7.07l.88.88"
                  stroke="currentColor"
                  strokeWidth="1.75"
                  strokeLinecap="round"
                />
              </svg>
              <input
                id="url-input"
                className="scanner-form__input"
                type="url"
                inputMode="url"
                autoComplete="url"
                placeholder="https://example.com"
                value={url}
                onChange={(event) => setUrl(event.target.value)}
                disabled={loading}
                aria-invalid={Boolean(error)}
                aria-describedby={error ? "scan-error" : undefined}
              />
            </div>
            <button
              className="scanner-form__button"
              type="submit"
              disabled={loading || !url.trim()}
            >
              {loading ? "Scanning…" : "Scan URL"}
            </button>
          </div>
          <p className="scanner-form__hint">
            Paste a full URL or domain name. Analysis may take a few seconds while
            features are extracted.
          </p>
        </form>

        {loading && <LoadingState />}

        {error && (
          <div className="scanner-alert scanner-alert--error" id="scan-error" role="alert">
            <strong>Scan failed.</strong> {error}
          </div>
        )}

        {result && !loading && (
          <ScanResultCard result={result} onAskAi={onAskAi} />
        )}
      </div>

      <footer className="scanner__footer">
        <p>Powered by CyberShield AI · XGBoost phishing detection</p>
      </footer>
    </main>
  );
}
