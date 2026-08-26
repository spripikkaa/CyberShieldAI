interface LoadingStateProps {
  title?: string;
  text?: string;
}

export default function LoadingState({
  title = "Scanning URL…",
  text = "Extracting features and running the phishing detection model.",
}: LoadingStateProps) {
  return (
    <div className="loading-state" role="status" aria-live="polite" aria-busy="true">
      <div className="loading-state__spinner" aria-hidden="true" />
      <div>
        <p className="loading-state__title">{title}</p>
        <p className="loading-state__text">{text}</p>
      </div>
    </div>
  );
}
