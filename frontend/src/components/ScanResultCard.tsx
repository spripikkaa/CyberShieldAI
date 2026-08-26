import type { ScanResult } from "../types/scan";
import { formatConfidence } from "../utils/recommendations";

interface ScanResultCardProps {
  result: ScanResult;
  onAskAi?: (result: ScanResult) => void;
}

function StatusIcon({ status }: { status: ScanResult["status"] }) {
  if (status === "safe") {
    return (
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.75" />
        <path
          d="M8.5 12.2L10.8 14.5L15.8 9.5"
          stroke="currentColor"
          strokeWidth="1.75"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    );
  }

  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M12 8.5V13"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
      <circle cx="12" cy="16.5" r="1" fill="currentColor" />
      <path
        d="M10.3 4.5L2.8 18.2C2.2 19.3 3 20.7 4.3 20.7H19.7C21 20.7 21.8 19.3 21.2 18.2L13.7 4.5C13.1 3.4 11.9 3.4 11.3 4.5H10.3Z"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default function ScanResultCard({ result, onAskAi }: ScanResultCardProps) {
  const statusLabel = result.status === "safe" ? "Safe" : "Phishing";

  return (
    <section
      className={`scan-result scan-result--${result.status}`}
      aria-live="polite"
    >
      <div className="scan-result__header">
        <div className={`scan-result__badge scan-result__badge--${result.status}`}>
          <StatusIcon status={result.status} />
          <span>{statusLabel}</span>
        </div>
        <p className="scan-result__confidence">
          Confidence: <strong>{formatConfidence(result.confidence)}</strong>
        </p>
      </div>

      <div className="scan-result__grid">
        <article className="scan-result__item">
          <span className="scan-result__label">Scanned URL</span>
          <p className="scan-result__url" title={result.url}>
            {result.url}
          </p>
        </article>

        <article className="scan-result__item">
          <span className="scan-result__label">Threat Status</span>
          <p className={`scan-result__value scan-result__value--${result.status}`}>
            {statusLabel}
          </p>
        </article>

        <article className="scan-result__item">
          <span className="scan-result__label">Confidence Score</span>
          <div className="scan-result__meter">
            <div
              className={`scan-result__meter-fill scan-result__meter-fill--${result.status}`}
              style={{ width: `${Math.round(result.confidence * 100)}%` }}
            />
          </div>
          <p className="scan-result__meter-value">{formatConfidence(result.confidence)}</p>
        </article>
      </div>

      <article className="scan-result__recommendation">
        <span className="scan-result__label">Security Recommendation</span>
        <p>{result.recommendation}</p>
      </article>

      {onAskAi && (
        <div className="scan-result__actions">
          <button
            type="button"
            className="scan-result__ask-ai"
            onClick={() => onAskAi(result)}
          >
            Explain with AI Assistant
          </button>
        </div>
      )}
    </section>
  );
}
