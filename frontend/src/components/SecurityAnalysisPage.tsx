import { FormEvent, useState } from "react";
import { ApiError } from "../api/client";
import {
  fetchDns,
  fetchExplain,
  fetchSsl,
  fetchWhois,
} from "../api/securityApi";
import type {
  DnsResult,
  ExplainResult,
  SecurityTab,
  SslResult,
  WhoisResult,
} from "../types/security";
import { formatConfidence } from "../utils/recommendations";
import LoadingState from "./LoadingState";

const TABS: { id: SecurityTab; label: string }[] = [
  { id: "whois", label: "WHOIS" },
  { id: "ssl", label: "SSL/TLS" },
  { id: "dns", label: "DNS" },
  { id: "explain", label: "AI Explain" },
];

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

function RecordList({
  title,
  items,
}: {
  title: string;
  items: string[];
}) {
  if (items.length === 0) {
    return (
      <article className="analysis-card">
        <span className="analysis-card__label">{title}</span>
        <p className="analysis-card__value analysis-card__value--muted">None found</p>
      </article>
    );
  }

  return (
    <article className="analysis-card analysis-card--wide">
      <span className="analysis-card__label">{title}</span>
      <ul className="analysis-card__list">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </article>
  );
}

function WhoisResults({ data }: { data: WhoisResult }) {
  return (
    <div className="analysis-grid">
      <article className="analysis-card">
        <span className="analysis-card__label">Domain</span>
        <p className="analysis-card__value">{data.domain_name}</p>
      </article>
      <article className="analysis-card">
        <span className="analysis-card__label">Registrar</span>
        <p className="analysis-card__value">{data.registrar ?? "Unknown"}</p>
      </article>
      <article className="analysis-card">
        <span className="analysis-card__label">Domain age</span>
        <p className="analysis-card__value">{data.domain_age ?? "Unknown"}</p>
      </article>
      <article className="analysis-card">
        <span className="analysis-card__label">Country</span>
        <p className="analysis-card__value">{data.country ?? "Unknown"}</p>
      </article>
      <article className="analysis-card">
        <span className="analysis-card__label">Created</span>
        <p className="analysis-card__value">{data.creation_date ?? "Unknown"}</p>
      </article>
      <article className="analysis-card">
        <span className="analysis-card__label">Expires</span>
        <p className="analysis-card__value">{data.expiration_date ?? "Unknown"}</p>
      </article>
    </div>
  );
}

function SslResults({ data }: { data: SslResult }) {
  const sslValid = data.ssl_status === "Valid";
  return (
    <div className="analysis-grid">
      <article className="analysis-card">
        <span className="analysis-card__label">SSL status</span>
        <p
          className={`analysis-card__value analysis-card__value--${sslValid ? "safe" : "danger"}`}
        >
          {data.ssl_status}
        </p>
      </article>
      <article className="analysis-card">
        <span className="analysis-card__label">HTTPS</span>
        <p className="analysis-card__value">{data.https_status}</p>
      </article>
      <article className="analysis-card">
        <span className="analysis-card__label">Issuer</span>
        <p className="analysis-card__value">{data.certificate_issuer ?? "Unknown"}</p>
      </article>
      <article className="analysis-card">
        <span className="analysis-card__label">Subject</span>
        <p className="analysis-card__value">{data.subject ?? "Unknown"}</p>
      </article>
      <article className="analysis-card">
        <span className="analysis-card__label">Valid from</span>
        <p className="analysis-card__value">{data.valid_from ?? "Unknown"}</p>
      </article>
      <article className="analysis-card">
        <span className="analysis-card__label">Expiry</span>
        <p className="analysis-card__value">
          {data.expiry_date ?? "Unknown"}
          {data.days_remaining != null && ` (${data.days_remaining} days left)`}
        </p>
      </article>
    </div>
  );
}

function DnsResults({ data }: { data: DnsResult }) {
  return (
    <div className="analysis-grid">
      <article className="analysis-card">
        <span className="analysis-card__label">Domain</span>
        <p className="analysis-card__value">{data.domain_name}</p>
      </article>
      <article className="analysis-card">
        <span className="analysis-card__label">Primary IP</span>
        <p className="analysis-card__value">{data.ip_address ?? "Unknown"}</p>
      </article>
      <RecordList title="A records" items={data.a_records} />
      <RecordList title="AAAA records" items={data.aaaa_records} />
      <RecordList title="MX records" items={data.mx_records} />
      <RecordList title="NS records" items={data.ns_records} />
      <RecordList title="CNAME records" items={data.cname} />
      <RecordList title="TXT records" items={data.txt_records} />
    </div>
  );
}

function ExplainResults({ data }: { data: ExplainResult }) {
  const isPhishing = data.prediction === "Phishing";

  return (
    <div className="analysis-explain">
      <div className="analysis-explain__summary">
        <span
          className={`history-card__badge history-card__badge--${isPhishing ? "phishing" : "safe"}`}
        >
          {data.prediction}
        </span>
        <p>
          Confidence: <strong>{formatConfidence(data.confidence)}</strong>
        </p>
      </div>

      <article className="analysis-card analysis-card--wide">
        <span className="analysis-card__label">AI explanation</span>
        <p className="analysis-card__text">{data.explanation}</p>
      </article>

      <div className="analysis-features">
        <h3 className="analysis-features__title">Top contributing features</h3>
        <div className="analysis-features__list">
          {data.top_10_important_features.map((feature) => (
            <article key={feature.feature} className="analysis-feature">
              <div className="analysis-feature__header">
                <span className="analysis-feature__name">{feature.feature}</span>
                <span
                  className={`analysis-feature__impact analysis-feature__impact--${feature.impact}`}
                >
                  {feature.impact.replaceAll("_", " ")}
                </span>
              </div>
              <div className="analysis-feature__bar">
                <div
                  className="analysis-feature__bar-fill"
                  style={{
                    width: `${Math.min(Math.abs(feature.shap_value) * 100, 100)}%`,
                  }}
                />
              </div>
              <p className="analysis-feature__meta">
                Value: {feature.feature_value.toFixed(3)} · SHAP:{" "}
                {feature.shap_value.toFixed(4)}
              </p>
            </article>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function SecurityAnalysisPage() {
  const [url, setUrl] = useState("");
  const [activeTab, setActiveTab] = useState<SecurityTab>("whois");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [whois, setWhois] = useState<WhoisResult | null>(null);
  const [ssl, setSsl] = useState<SslResult | null>(null);
  const [dns, setDns] = useState<DnsResult | null>(null);
  const [explain, setExplain] = useState<ExplainResult | null>(null);

  async function handleAnalyze(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    const normalizedUrl = normalizeUrlInput(url);
    if (!normalizedUrl) {
      setError("Please enter a URL to analyze.");
      return;
    }

    if (!isValidUrl(normalizedUrl)) {
      setError("Enter a valid website URL (for example, https://example.com).");
      return;
    }

    setLoading(true);
    setWhois(null);
    setSsl(null);
    setDns(null);
    setExplain(null);

    try {
      if (activeTab === "whois") {
        setWhois(await fetchWhois(normalizedUrl));
      } else if (activeTab === "ssl") {
        setSsl(await fetchSsl(normalizedUrl));
      } else if (activeTab === "dns") {
        setDns(await fetchDns(normalizedUrl));
      } else {
        setExplain(await fetchExplain(normalizedUrl));
      }
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else if (err instanceof TypeError) {
        setError("Unable to reach the backend. Check that the API server is running.");
      } else {
        setError("Analysis failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  const hasResults = Boolean(whois || ssl || dns || explain);

  return (
    <section className="page-panel">
      <header className="page-panel__header">
        <p className="page-panel__eyebrow">Security Analysis</p>
        <h2 className="page-panel__title">Deep domain intelligence</h2>
        <p className="page-panel__subtitle">
          Inspect registration data, certificates, DNS records, and AI-powered
          explanations for any URL.
        </p>
      </header>

      <div className="analysis-tabs" role="tablist" aria-label="Analysis type">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={activeTab === tab.id}
            className={`analysis-tabs__item${activeTab === tab.id ? " analysis-tabs__item--active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <form className="scanner-form analysis-form" onSubmit={handleAnalyze} noValidate>
        <label className="scanner-form__label" htmlFor="analysis-url">
          Target URL
        </label>
        <div className="scanner-form__row">
          <div className="scanner-form__input-wrap">
            <input
              id="analysis-url"
              className="scanner-form__input scanner-form__input--plain"
              type="url"
              inputMode="url"
              autoComplete="url"
              placeholder="https://example.com"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              disabled={loading}
            />
          </div>
          <button
            className="scanner-form__button"
            type="submit"
            disabled={loading || !url.trim()}
          >
            {loading ? "Analyzing…" : "Run analysis"}
          </button>
        </div>
      </form>

      {loading && (
        <LoadingState
          title="Running analysis…"
          text={
            activeTab === "explain"
              ? "Generating SHAP-based AI explanation for this URL."
              : `Querying ${activeTab.toUpperCase()} intelligence for the target domain.`
          }
        />
      )}

      {error && (
        <div className="scanner-alert scanner-alert--error" role="alert">
          <strong>Analysis failed.</strong> {error}
        </div>
      )}

      {!loading && hasResults && (
        <div className="analysis-results">
          {whois && <WhoisResults data={whois} />}
          {ssl && <SslResults data={ssl} />}
          {dns && <DnsResults data={dns} />}
          {explain && <ExplainResults data={explain} />}
        </div>
      )}
    </section>
  );
}
