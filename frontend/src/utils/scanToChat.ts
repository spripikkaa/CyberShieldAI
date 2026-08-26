import type { ChatScanResult } from "../types/chatbot";
import type { ScanResult } from "../types/scan";

export function scanResultToChatPayload(result: ScanResult): ChatScanResult {
  return {
    prediction: result.prediction,
    url: result.url,
    confidence: result.confidence,
    reasons: [result.recommendation],
  };
}
