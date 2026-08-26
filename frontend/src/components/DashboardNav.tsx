export type DashboardView = "scanner" | "history" | "analysis" | "chat";

export interface NavItem {
  id: DashboardView;
  label: string;
  description: string;
  icon: "scanner" | "history" | "analysis" | "chat";
}

export const NAV_ITEMS: NavItem[] = [
  {
    id: "scanner",
    label: "URL Scanner",
    description: "Phishing detection",
    icon: "scanner",
  },
  {
    id: "history",
    label: "Scan History",
    description: "Past scan reports",
    icon: "history",
  },
  {
    id: "analysis",
    label: "Security Analysis",
    description: "WHOIS, SSL, DNS & AI",
    icon: "analysis",
  },
  {
    id: "chat",
    label: "AI Assistant",
    description: "Cybersecurity chatbot",
    icon: "chat",
  },
];

function NavIcon({ icon }: { icon: NavItem["icon"] }) {
  if (icon === "scanner") {
    return (
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 2L4 5.5V11.5C4 16.42 7.13 20.95 12 22C16.87 20.95 20 16.42 20 11.5V5.5L12 2Z"
          stroke="currentColor"
          strokeWidth="1.75"
          strokeLinejoin="round"
        />
      </svg>
    );
  }

  if (icon === "history") {
    return (
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.75" />
        <path
          d="M12 7V12L15 14"
          stroke="currentColor"
          strokeWidth="1.75"
          strokeLinecap="round"
        />
      </svg>
    );
  }

  if (icon === "analysis") {
    return (
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M4 19V5M4 19H20M8 15V11M12 15V7M16 15V9"
          stroke="currentColor"
          strokeWidth="1.75"
          strokeLinecap="round"
        />
      </svg>
    );
  }

  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M12 2l8 3v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V5l8-3z"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinejoin="round"
      />
      <path
        d="M8 10h8M8 14h5"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
    </svg>
  );
}

interface DashboardNavProps {
  activeView: DashboardView;
  onNavigate: (view: DashboardView) => void;
}

export default function DashboardNav({ activeView, onNavigate }: DashboardNavProps) {
  return (
    <nav className="dashboard-nav" aria-label="Dashboard">
      {NAV_ITEMS.map((item) => (
        <button
          key={item.id}
          type="button"
          className={`dashboard-nav__item${activeView === item.id ? " dashboard-nav__item--active" : ""}`}
          onClick={() => onNavigate(item.id)}
          aria-current={activeView === item.id ? "page" : undefined}
        >
          <span className="dashboard-nav__icon">
            <NavIcon icon={item.icon} />
          </span>
          <span className="dashboard-nav__text">
            <span className="dashboard-nav__label">{item.label}</span>
            <span className="dashboard-nav__description">{item.description}</span>
          </span>
        </button>
      ))}
    </nav>
  );
}
