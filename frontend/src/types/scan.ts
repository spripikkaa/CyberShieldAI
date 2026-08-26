export type PredictionLabel = "Legitimate" | "Phishing";

export interface PredictResponse {
  prediction: PredictionLabel;
  confidence: number;
}

export type ScanStatus = "safe" | "phishing";

export interface ScanResult {
  url: string;
  status: ScanStatus;
  prediction: PredictionLabel;
  confidence: number;
  recommendation: string;
}

export interface ScanError {
  message: string;
}
