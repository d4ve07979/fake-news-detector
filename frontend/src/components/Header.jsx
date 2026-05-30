import { useEffect, useState } from "react";

const IconSearch = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
  </svg>
);
const IconChart = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
  </svg>
);
const IconList = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/>
    <line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>
  </svg>
);

export default function Header({ tab, setTab }) {
  const [apiOk, setApiOk] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/health")
      .then(r => r.json())
      .then(d => setApiOk(d.model_loaded))
      .catch(() => setApiOk(false));
  }, []);

  const tabs = [
    { id: "analyzer",  label: "Analyser",   Icon: IconSearch },
    { id: "dashboard", label: "Dashboard",  Icon: IconChart  },
    { id: "history",   label: "Historique", Icon: IconList   },
  ];

  return (
    <header className="header">
      <div className="header-inner">
        <div className="header-logo">
          <div className="logo-badge">FN</div>
          <div>
            <div className="logo-text">Fake News Detector</div>
            <div className="logo-sub">Powered by BERT · L3 IA &amp; Big Data</div>
          </div>
        </div>
        <nav className="header-nav">
          {tabs.map(({ id, label, Icon }) => (
            <button
              key={id}
              className={`nav-btn${tab === id ? " active" : ""}`}
              onClick={() => setTab(id)}
            >
              <Icon />
              <span>{label}</span>
            </button>
          ))}
        </nav>
        <div
          className="status-dot"
          title={apiOk === null ? "Vérification..." : apiOk ? "API connectée" : "API hors ligne"}
          style={{ background: apiOk === null ? "#f59e0b" : apiOk ? "#22c55e" : "#ef4444",
                   boxShadow: `0 0 6px ${apiOk ? "#22c55e" : "#ef4444"}` }}
        />
      </div>
    </header>
  );
}
