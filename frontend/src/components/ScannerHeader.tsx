function ShieldIcon() {
  return (
    <svg
      className="scanner-header__icon"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <path
        d="M12 2L4 5.5V11.5C4 16.42 7.13 20.95 12 22C16.87 20.95 20 16.42 20 11.5V5.5L12 2Z"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinejoin="round"
      />
      <path
        d="M9.5 12.2L11.1 13.8L14.8 10.1"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default function ScannerHeader() {
  return (
    <header className="scanner-header">
      <div className="scanner-header__brand">
        <ShieldIcon />
        <div>
          <p className="scanner-header__eyebrow">CyberShield AI</p>
          <h1 className="scanner-header__title">URL Threat Scanner</h1>
        </div>
      </div>
      <p className="scanner-header__subtitle">
        Analyze any website URL with machine learning to detect phishing threats before
        you click.
      </p>
    </header>
  );
}
