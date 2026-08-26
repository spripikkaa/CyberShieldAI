export interface ChatScanResult {
  prediction: string;
  reasons: string[];
  confidence?: number;
  url?: string;
}

export interface ChatMessage {
  sender: "user" | "bot";
  text: string;
  timestamp: Date;
  isError?: boolean;
}

export interface ChatResponse {
  reply: string;
  is_scan_explanation: boolean;
  conversation_id: string;
}
