import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type Dispatch,
  type SetStateAction,
} from "react";
import {
  clearConversation,
  sendChatMessage,
  sendScanResult,
} from "../../api/chatbotApi";
import type { ChatMessage, ChatScanResult } from "../../types/chatbot";
import ChatHeader from "./ChatHeader";
import ChatInput from "./ChatInput";
import ChatMessageView from "./ChatMessage";
import SuggestedQuestions from "./SuggestedQuestions";
import TypingIndicator from "./TypingIndicator";

interface ChatbotWindowProps {
  onClose?: () => void;
  embedded?: boolean;
  initialScanResult?: ChatScanResult | string | null;
  messages: ChatMessage[];
  setMessages: Dispatch<SetStateAction<ChatMessage[]>>;
  conversationId: string | null;
  onStartNewConversation: () => void;
}

export default function ChatbotWindow({
  onClose,
  embedded = false,
  initialScanResult = null,
  messages,
  setMessages,
  conversationId,
  onStartNewConversation,
}: ChatbotWindowProps) {
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const lastSentScanRef = useRef<string | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const handleSend = useCallback(
    async (text: string) => {
      const userMessage: ChatMessage = {
        sender: "user",
        text,
        timestamp: new Date(),
      };

      setMessages((previous) => [...previous, userMessage]);
      setIsTyping(true);

      try {
        const { reply } = await sendChatMessage(text, conversationId);
        setMessages((previous) => [
          ...previous,
          {
            sender: "bot",
            text: reply,
            timestamp: new Date(),
          },
        ]);
      } catch (error) {
        const message =
          error instanceof Error
            ? error.message
            : "Something went wrong while contacting the assistant. Please try again.";

        setMessages((previous) => [
          ...previous,
          {
            sender: "bot",
            text: message,
            timestamp: new Date(),
            isError: true,
          },
        ]);
      } finally {
        setIsTyping(false);
      }
    },
    [conversationId, setMessages],
  );

  const handleSendScanResult = useCallback(
    async (scanResult: ChatScanResult) => {
      const summaryText = `Scan result: ${scanResult.prediction}${
        scanResult.url ? ` — ${scanResult.url}` : ""
      }`;

      setMessages((previous) => [
        ...previous,
        {
          sender: "user",
          text: summaryText,
          timestamp: new Date(),
        },
      ]);
      setIsTyping(true);

      try {
        const { reply } = await sendScanResult(scanResult, conversationId);
        setMessages((previous) => [
          ...previous,
          {
            sender: "bot",
            text: reply,
            timestamp: new Date(),
          },
        ]);
      } catch (error) {
        const message =
          error instanceof Error
            ? error.message
            : "Something went wrong explaining this scan result.";

        setMessages((previous) => [
          ...previous,
          {
            sender: "bot",
            text: message,
            timestamp: new Date(),
            isError: true,
          },
        ]);
      } finally {
        setIsTyping(false);
      }
    },
    [conversationId, setMessages],
  );

  useEffect(() => {
    if (!initialScanResult || !conversationId) {
      return;
    }

    const scanKey =
      typeof initialScanResult === "string"
        ? initialScanResult
        : JSON.stringify(initialScanResult);

    if (lastSentScanRef.current === scanKey) {
      return;
    }

    lastSentScanRef.current = scanKey;

    if (typeof initialScanResult === "string") {
      void handleSend(initialScanResult);
      return;
    }

    void handleSendScanResult(initialScanResult);
  }, [conversationId, handleSend, handleSendScanResult, initialScanResult]);

  async function handleClear() {
    if (conversationId) {
      await clearConversation(conversationId);
    }
    lastSentScanRef.current = null;
    onStartNewConversation();
  }

  const showSuggestions = messages.length === 1;

  return (
    <div
      className="cs-chatbot-window"
      role="dialog"
      aria-label="CyberShield AI Assistant chat"
    >
      <ChatHeader
        onClose={onClose}
        onClear={() => {
          void handleClear();
        }}
        embedded={embedded}
      />

      <div className="cs-chat-body">
        <div className="cs-chat-messages">
          {messages.map((message, index) => (
            <ChatMessageView
              key={`${message.timestamp.getTime()}-${index}`}
              sender={message.sender}
              text={message.text}
              timestamp={message.timestamp}
              isError={message.isError}
            />
          ))}

          {isTyping && <TypingIndicator />}

          {showSuggestions && !isTyping && (
            <SuggestedQuestions onSelect={(question) => void handleSend(question)} />
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      <ChatInput
        onSend={(text) => void handleSend(text)}
        disabled={isTyping || !conversationId}
      />
    </div>
  );
}
