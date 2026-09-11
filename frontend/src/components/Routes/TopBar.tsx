import type { StatusInfo } from "@/hooks/useRouteBuilder";

interface TopBarProps {
  status: StatusInfo;
}

export function TopBar({ status }: TopBarProps) {
  return (
    <header className="topbar">
      <div className="brand">
        <div className="brand-mark">🛣️</div>
        <div className="brand-text">
          <div className="brand-name">Routes API Demo</div>
          <div className="brand-sub">Vector8 OSRM Integration</div>
        </div>
      </div>
      <div className="topbar-right">
        <div className="preview-pill">Демо UI</div>
        <div className="status">
          <span className={`status-dot ${status.kind}`} />
          <span>{status.label}</span>
        </div>
      </div>
    </header>
  );
}

