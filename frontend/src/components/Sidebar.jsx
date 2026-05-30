import { useEffect, useState } from "react";
import axios from "axios";

const API = "http://localhost:8000";

const icons = {
  home:      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>,
  analyzer:  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>,
  dashboard: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>,
  history:   <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>,
  about:     <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>,
};

const SECTIONS = [
  { label:"Principal", items:[
    { id:"home",      label:"Accueil"    },
    { id:"analyzer",  label:"Analyser"   },
    { id:"dashboard", label:"Dashboard"  },
  ]},
  { label:"Données", items:[
    { id:"history",  label:"Historique" },
  ]},
  { label:"Projet", items:[
    { id:"about",    label:"À propos"   },
  ]},
];

export default function Sidebar({ page, setPage, open, mobileOpen }) {
  const [status, setStatus] = useState("loading");
  const [model,  setModel]  = useState("v1.0.0");

  useEffect(() => {
    const check = () =>
      axios.get(`${API}/health`, { timeout:3000 })
        .then(r => { setStatus(r.data.model_loaded ? "online" : "offline"); if (r.data.model_version) setModel(`v${r.data.model_version}`); })
        .catch(() => setStatus("offline"));
    check();
    const t = setInterval(check, 30000);
    return () => clearInterval(t);
  }, []);

  const cls = ["sidebar", !open ? "closed" : "", mobileOpen ? "mobile-open" : ""].filter(Boolean).join(" ");

  return (
    <aside className={cls}>
      <div className="sidebar-logo">
        <div className="logo-icon">FN</div>
        <div>
          <div className="logo-name">FakeDetect</div>
          <div className="logo-badge">L3 IA &amp; Big Data</div>
        </div>
      </div>

      <div style={{ overflowY:"auto", flex:1 }}>
        {SECTIONS.map(({ label, items }) => (
          <div key={label} className="sidebar-section">
            <div className="sidebar-section-label">{label}</div>
            {items.map(({ id, label: lbl }) => (
              <button key={id}
                className={"sidebar-nav-item" + (page === id ? " active" : "")}
                onClick={() => setPage(id)}
              >
                {icons[id]}
                <span>{lbl}</span>
              </button>
            ))}
          </div>
        ))}
      </div>

      <div className="sidebar-footer">
        <div className="sidebar-status">
          <div className={"status-indicator " + status} />
          <div>
            <div className="status-text">{status==="online" ? "API connectée" : status==="offline" ? "Hors ligne" : "Connexion..."}</div>
            <div className="status-model">{model}</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
