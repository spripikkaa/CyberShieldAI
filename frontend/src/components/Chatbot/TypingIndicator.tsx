export default function TypingIndicator() {
  return (
    <div className="cs-msg-row cs-msg-row--bot">
      <div className="cs-msg-avatar cs-msg-avatar--bot">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 2l8 3v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V5l8-3z" strokeLinejoin="round" />
        </svg>
      </div>
      <div className="cs-msg-bubble cs-msg-bubble--bot cs-typing">
        <span className="cs-typing__dot" />
        <span className="cs-typing__dot" />
        <span className="cs-typing__dot" />
      </div>
    </div>
  );
}
