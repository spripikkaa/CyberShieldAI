import { useCallback, useEffect, useState } from "react";
import type { ChatMessage, ChatScanResult } from "../../types/chatbot";
import ChatbotButton from "./ChatbotButton";
import ChatbotWindow from "./ChatbotWindow";
import "./Chatbot.css";

const SESSION_STORAGE_KEY = "cybershield_chatbot_conversation_id";

const WELCOME_MESSAGE: ChatMessage = {
  sender: "bot",
  text:
    "**CyberShield AI Assistant**\n\nHello! I'm your cybersecurity assistant.\n\nI can:\n" +
    "- Explain phishing scan results\n" +
    "- Answer cybersecurity questions\n" +
    "- Explain SSL, DNS and WHOIS\n" +
    "- Help you use CyberShield AI\n" +
    "- Provide online safety tips",
  timestamp: new Date(),
};

function generateId(): string {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }

  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (character) => {
    const random = (Math.random() * 16) | 0;
    const value = character === "x" ? random : (random & 0x3) | 0x8;
    return value.toString(16);
  });
}

export interface CyberShieldChatbotProps {
  mode?: "widget" | "embedded";
  initialScanResult?: ChatScanResult | string | null;
}

export default function CyberShieldChatbot({
  mode = "widget",
  initialScanResult = null,
}: CyberShieldChatbotProps) {
  const embedded = mode === "embedded";
  const [isOpen, setIsOpen] = useState(embedded);
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [conversationId, setConversationId] = useState<string | null>(null);

  useEffect(() => {
    let stored: string | null = null;

    try {
      stored = sessionStorage.getItem(SESSION_STORAGE_KEY);
    } catch {
      stored = null;
    }

    const id = stored || generateId();
    setConversationId(id);

    try {
      sessionStorage.setItem(SESSION_STORAGE_KEY, id);
    } catch {
      /* non-fatal */
    }
  }, []);

  const startNewConversation = useCallback(() => {
    const newId = generateId();
    setConversationId(newId);
    setMessages([WELCOME_MESSAGE]);

    try {
      sessionStorage.setItem(SESSION_STORAGE_KEY, newId);
    } catch {
      /* non-fatal */
    }
  }, []);

  return (
    <div
      className={`cs-chatbot-root ${
        embedded ? "cs-chatbot-root--embedded" : "cs-chatbot-root--widget"
      }`}
    >
      {(embedded || isOpen) && (
        <ChatbotWindow
          embedded={embedded}
          onClose={embedded ? undefined : () => setIsOpen(false)}
          initialScanResult={initialScanResult}
          messages={messages}
          setMessages={setMessages}
          conversationId={conversationId}
          onStartNewConversation={startNewConversation}
        />
      )}

      {!embedded && (
        <ChatbotButton
          isOpen={isOpen}
          onClick={() => setIsOpen((previous) => !previous)}
        />
      )}
    </div>
  );
}
