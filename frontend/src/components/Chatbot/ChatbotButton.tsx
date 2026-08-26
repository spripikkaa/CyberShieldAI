import "./Chatbot.css";

interface ChatbotButtonProps {
  isOpen: boolean;
  onClick: () => void;
}

export default function ChatbotButton({ isOpen, onClick }: ChatbotButtonProps) {
  return (
    <button
      type="button"
      className={`cs-chatbot-fab ${isOpen ? "cs-chatbot-fab--open" : ""}`}
      onClick={onClick}
      aria-label={
        isOpen
          ? "Close CyberShield AI Assistant"
          : "Open CyberShield AI Assistant"
      }
      title={isOpen ? "Close chat" : "Chat with CyberShield AI"}
    >
      <span className="cs-chatbot-fab__icon-wrapper">
        {isOpen ? (
          <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18" strokeLinecap="round" />
            <line x1="6" y1="6" x2="18" y2="18" strokeLinecap="round" />
          </svg>
        ) : (
          <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" strokeWidth="2">
            <path
              d="M12 2l8 3v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V5l8-3z"
              strokeLinejoin="round"
            />
            <path d="M9 12l2 2 4-4" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        )}
      </span>
      {!isOpen && <span className="cs-chatbot-fab__pulse" />}
    </button>
  );
}
