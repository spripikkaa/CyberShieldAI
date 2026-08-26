import CyberShieldChatbot from "./Chatbot";
import type { ChatScanResult } from "../types/chatbot";

interface ChatAssistantPageProps {
  initialScanResult?: ChatScanResult | null;
}

export default function ChatAssistantPage({
  initialScanResult = null,
}: ChatAssistantPageProps) {
  return (
    <section className="chat-assistant-page">
      <header className="chat-assistant-page__header">
        <p className="chat-assistant-page__eyebrow">CyberShield AI</p>
        <h1>AI Security Assistant</h1>
        <p className="chat-assistant-page__subtitle">
          Ask cybersecurity questions, learn about phishing, or get help
          understanding your latest URL scan results.
        </p>
      </header>

      <div className="chat-assistant-page__panel">
        <CyberShieldChatbot
          mode="embedded"
          initialScanResult={initialScanResult}
        />
      </div>
    </section>
  );
}
