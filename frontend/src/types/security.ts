import type { PredictionLabel } from "./scan";

export interface ScanReport {
  id: string;
  user_id: string;
  url: string;
  prediction: PredictionLabel;
  confidence: number;
  timestamp: string;
}

export interface WhoisResult {
  domain_name: string;
  registrar: string | null;
  creation_date: string | null;
  expiration_date: string | null;
  domain_age: string | null;
  country: string | null;
}

export interface SslResult {
  ssl_status: "Valid" | "Invalid";
  https_status: "Enabled" | "Disabled";
  certificate_issuer: string | null;
  subject: string | null;
  valid_from: string | null;
  expiry_date: string | null;
  days_remaining: number | null;
  signature_algorithm: string | null;
}

export interface DnsResult {
  domain_name: string;
  ip_address: string | null;
  a_records: string[];
  aaaa_records: string[];
  mx_records: string[];
  ns_records: string[];
  cname: string[];
  txt_records: string[];
}

export interface FeatureContribution {
  feature: string;
  feature_value: number;
  shap_value: number;
  impact: "toward_phishing" | "toward_legitimate" | "neutral";
}

export interface ExplainResult {
  prediction: PredictionLabel;
  confidence: number;
  top_10_important_features: FeatureContribution[];
  shap_values: Record<string, number>;
  feature_importance: Record<string, number>;
  explanation: string;
}

export type SecurityTab = "whois" | "ssl" | "dns" | "explain";
