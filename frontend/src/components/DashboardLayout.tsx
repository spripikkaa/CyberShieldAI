import type { ReactNode } from "react";
import { useAuth } from "../context/AuthContext";
import DashboardNav, { type DashboardView } from "./DashboardNav";

interface DashboardLayoutProps {
  activeView: DashboardView;
  onNavigate: (view: DashboardView) => void;
  children: ReactNode;
}

function ShieldLogo() {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
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

export default function DashboardLayout({
  activeView,
  onNavigate,
  children,
}: DashboardLayoutProps) {
  const { user, logout } = useAuth();

  return (
    <div className="dashboard">
      <aside className="dashboard__sidebar">
        <div className="dashboard__brand">
          <span className="dashboard__brand-icon">
            <ShieldLogo />
          </span>
          <div>
            <p className="dashboard__brand-eyebrow">CyberShield AI</p>
            <p className="dashboard__brand-title">Security Dashboard</p>
          </div>
        </div>

        <DashboardNav activeView={activeView} onNavigate={onNavigate} />

        <div className="dashboard__sidebar-footer">
          {user && (
            <div className="dashboard__user">
              <div className="dashboard__user-avatar" aria-hidden="true">
                {user.name.charAt(0).toUpperCase()}
              </div>
              <div className="dashboard__user-info">
                <p className="dashboard__user-name">{user.name}</p>
                <p className="dashboard__user-email">{user.email}</p>
              </div>
              <button
                type="button"
                className="dashboard__logout"
                onClick={logout}
              >
                Sign out
              </button>
            </div>
          )}
        </div>
      </aside>

      <div className="dashboard__main">{children}</div>
    </div>
  );
}
