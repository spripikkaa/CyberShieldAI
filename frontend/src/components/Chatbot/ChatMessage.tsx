function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function renderMarkdown(text: string): string {
  let safe = escapeHtml(text);

  safe = safe.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  safe = safe.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, "<em>$1</em>");

  const lines = safe.split("\n");
  let html = "";
  let inList = false;

  lines.forEach((line) => {
    const bulletMatch = line.match(/^\s*[-*]\s+(.*)/);

    if (bulletMatch) {
      if (!inList) {
        html += "<ul>";
        inList = true;
      }
      html += `<li>${bulletMatch[1]}</li>`;
    } else {
      if (inList) {
        html += "</ul>";
        inList = false;
      }
      html += line.trim() === "" ? "<br/>" : `<p>${line}</p>`;
    }
  });

  if (inList) {
    html += "</ul>";
  }

  return html;
}

function formatTime(date: Date): string {
  return new Date(date).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

interface ChatMessageProps {
  sender: "user" | "bot";
  text: string;
  timestamp: Date;
  isError?: boolean;
}

export default function ChatMessage({
  sender,
  text,
  timestamp,
  isError = false,
}: ChatMessageProps) {
  const isUser = sender === "user";

  return (
    <div className={`cs-msg-row ${isUser ? "cs-msg-row--user" : "cs-msg-row--bot"}`}>
      {!isUser && (
        <div className="cs-msg-avatar cs-msg-avatar--bot">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2l8 3v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V5l8-3z" strokeLinejoin="round" />
          </svg>
        </div>
      )}

      <div
        className={`cs-msg-bubble ${isUser ? "cs-msg-bubble--user" : "cs-msg-bubble--bot"} ${
          isError ? "cs-msg-bubble--error" : ""
        }`}
      >
        {isUser ? (
          <p className="cs-msg-text">{text}</p>
        ) : (
          <div
            className="cs-msg-text cs-msg-text--markdown"
            dangerouslySetInnerHTML={{ __html: renderMarkdown(text) }}
          />
        )}
        <span className="cs-msg-timestamp">{formatTime(timestamp)}</span>
      </div>

      {isUser && (
        <div className="cs-msg-avatar cs-msg-avatar--user">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="8" r="4" />
            <path d="M4 20c0-4 3.5-7 8-7s8 3 8 7" strokeLinecap="round" />
          </svg>
        </div>
      )}
    </div>
  );
}
