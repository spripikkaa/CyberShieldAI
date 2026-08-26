import { useState } from "react";
import AuthScreen from "./components/AuthScreen";
import ChatAssistantPage from "./components/ChatAssistantPage";
import CyberShieldChatbot from "./components/Chatbot";
import DashboardLayout from "./components/DashboardLayout";
import ScanHistoryPage from "./components/ScanHistoryPage";
import SecurityAnalysisPage from "./components/SecurityAnalysisPage";
import UrlScanner from "./components/UrlScanner";
import type { DashboardView } from "./components/DashboardNav";
import { useAuth } from "./context/AuthContext";
import type { ChatScanResult } from "./types/chatbot";
import type { ScanResult } from "./types/scan";
import { scanResultToChatPayload } from "./utils/scanToChat";

export default function App() {
  const { isAuthenticated } = useAuth();
  const [activeView, setActiveView] = useState<DashboardView>("scanner");
  const [latestScanForChat, setLatestScanForChat] = useState<ChatScanResult | null>(
    null,
  );
  const [widgetScanResult, setWidgetScanResult] = useState<ChatScanResult | null>(
    null,
  );

  if (!isAuthenticated) {
    return <AuthScreen />;
  }

  function handleNavigate(view: DashboardView) {
    setActiveView(view);
  }

  function handleScanComplete(result: ScanResult) {
    const payload = scanResultToChatPayload(result);
    setLatestScanForChat(payload);
    setWidgetScanResult(payload);
  }

  function handleAskAiAboutScan(result: ScanResult) {
    const payload = scanResultToChatPayload(result);
    setLatestScanForChat(payload);
    setWidgetScanResult(payload);
    setActiveView("chat");
  }

  return (
    <div className="app-shell">
      <div className="app-background" aria-hidden="true">
        <div className="app-grid" />
        <div className="app-glow app-glow--left" />
        <div className="app-glow app-glow--right" />
      </div>

      <DashboardLayout activeView={activeView} onNavigate={handleNavigate}>
        {activeView === "scanner" && (
          <UrlScanner
            onScanComplete={handleScanComplete}
            onAskAi={handleAskAiAboutScan}
          />
        )}
        {activeView === "history" && <ScanHistoryPage />}
        {activeView === "analysis" && <SecurityAnalysisPage />}
        {activeView === "chat" && (
          <ChatAssistantPage initialScanResult={latestScanForChat} />
        )}
      </DashboardLayout>

      {activeView !== "chat" && (
        <CyberShieldChatbot initialScanResult={widgetScanResult} />
      )}
    </div>
  );
}
