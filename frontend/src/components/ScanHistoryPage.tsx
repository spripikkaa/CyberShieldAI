import { useCallback, useEffect, useState } from "react";
import { ApiError } from "../api/client";
import { fetchScanReports } from "../api/scanReportsApi";
import { useAuth } from "../context/AuthContext";
import type { ScanReport } from "../types/security";
import { formatConfidence } from "../utils/recommendations";
import LoadingState from "./LoadingState";


interface ScanHistoryPageProps {}

function formatTimestamp(value: string): string {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export default function ScanHistoryPage(_props: ScanHistoryPageProps) {
  const { userId } = useAuth();
  const [reports, setReports] = useState<ScanReport[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadReports = useCallback(async () => {
    if (!userId) return;

    setLoading(true);
    setError(null);

    try {
      const data = await fetchScanReports(userId);
      setReports(data);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else if (err instanceof TypeError) {
        setError("Unable to reach the backend. Check that the API server is running.");
      } else {
        setError("Failed to load scan history.");
      }
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    void loadReports();
  }, [loadReports]);

  return (
    <section className="page-panel">
      <header className="page-panel__header page-panel__header--row">
        <div>
          <p className="page-panel__eyebrow">Scan History</p>
          <h2 className="page-panel__title">Your saved scan reports</h2>
          <p className="page-panel__subtitle">
            Scans performed while signed in are stored automatically.
          </p>
        </div>
        <button
          type="button"
          className="page-panel__refresh"
          onClick={() => void loadReports()}
          disabled={loading}
        >
          Refresh
        </button>
      </header>

      {loading && (
        <LoadingState
          title="Loading scan history…"
          text="Fetching your saved phishing detection reports."
        />
      )}

      {error && (
        <div className="scanner-alert scanner-alert--error" role="alert">
          <strong>Unable to load history.</strong> {error}
        </div>
      )}

      {!loading && !error && reports.length === 0 && (
        <div className="page-panel__empty">
          <p>No scan reports yet. Run a URL scan while signed in to build your history.</p>
        </div>
      )}

      {!loading && reports.length > 0 && (
        <>
          <div className="history-stats" aria-label="Scan summary">
            <article className="history-stat">
              <span className="history-stat__label">Total scans</span>
              <strong className="history-stat__value">{reports.length}</strong>
            </article>
            <article className="history-stat history-stat--safe">
              <span className="history-stat__label">Legitimate</span>
              <strong className="history-stat__value">
                {reports.filter((report) => report.prediction === "Legitimate").length}
              </strong>
            </article>
            <article className="history-stat history-stat--phishing">
              <span className="history-stat__label">Phishing</span>
              <strong className="history-stat__value">
                {reports.filter((report) => report.prediction === "Phishing").length}
              </strong>
            </article>
          </div>

          <div className="history-list">
          {reports.map((report) => {
            const isPhishing = report.prediction === "Phishing";
            return (
              <article
                key={report.id}
                className={`history-card history-card--${isPhishing ? "phishing" : "safe"}`}
              >
                <div className="history-card__top">
                  <span
                    className={`history-card__badge history-card__badge--${isPhishing ? "phishing" : "safe"}`}
                  >
                    {report.prediction}
                  </span>
                  <time className="history-card__time" dateTime={report.timestamp}>
                    {formatTimestamp(report.timestamp)}
                  </time>
                </div>
                <p className="history-card__url" title={report.url}>
                  {report.url}
                </p>
                <p className="history-card__confidence">
                  Confidence: <strong>{formatConfidence(report.confidence)}</strong>
                </p>
              </article>
            );
          })}
          </div>
        </>
      )}
    </section>
  );
}
