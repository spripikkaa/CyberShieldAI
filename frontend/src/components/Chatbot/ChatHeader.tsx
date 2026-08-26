interface ChatHeaderProps {
  onClose?: () => void;
  onClear: () => void;
  embedded?: boolean;
}

export default function ChatHeader({
  onClose,
  onClear,
  embedded = false,
}: ChatHeaderProps) {
  return (
    <div className="cs-chat-header">
      <div className="cs-chat-header__brand">
        <span className="cs-chat-header__icon">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2l8 3v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V5l8-3z" strokeLinejoin="round" />
            <path d="M9 12l2 2 4-4" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </span>
        <div className="cs-chat-header__text">
          <h3>CyberShield AI Assistant</h3>
          <span className="cs-chat-header__status">
            <span className="cs-chat-header__status-dot" />
            Online
          </span>
        </div>
      </div>

      <div className="cs-chat-header__actions">
        <button
          type="button"
          className="cs-chat-header__btn cs-chat-header__btn--clear"
          onClick={onClear}
          title="Clear conversation"
          aria-label="Clear conversation"
        >
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="3 6 5 6 21 6" strokeLinecap="round" />
            <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
          </svg>
          Clear
        </button>
        {!embedded && onClose && (
          <button
            type="button"
            className="cs-chat-header__btn"
            onClick={onClose}
            title="Close"
            aria-label="Close chat"
          >
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18" strokeLinecap="round" />
              <line x1="6" y1="6" x2="18" y2="18" strokeLinecap="round" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
