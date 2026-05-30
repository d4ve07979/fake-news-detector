import { useState, useEffect } from "react";
import Sidebar   from "./components/Sidebar";
import Topbar    from "./components/Topbar";
import Landing   from "./components/Landing";
import Analyzer  from "./components/Analyzer";
import Dashboard from "./components/Dashboard";
import History   from "./components/History";
import About     from "./components/About";
import "./app.css";

export default function App() {
  const [page,          setPage]          = useState("home");
  const [theme,         setTheme]         = useState(() => localStorage.getItem("theme") || "dark");
  const [sidebarOpen,   setSidebarOpen]   = useState(true);
  const [mobileSidebar, setMobileSidebar] = useState(false);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  useEffect(() => {
    const handler = () => { if (window.innerWidth < 769) setSidebarOpen(false); };
    handler();
    window.addEventListener("resize", handler);
    return () => window.removeEventListener("resize", handler);
  }, []);

  const navigate = (p) => { setPage(p); setMobileSidebar(false); };

  return (
    <div className="app-shell">
      <Sidebar
        page={page} setPage={navigate}
        open={sidebarOpen} mobileOpen={mobileSidebar}
        onMobileClose={() => setMobileSidebar(false)}
      />
      <div className={"app-body" + (sidebarOpen ? " sidebar-open" : " sidebar-closed")}>
        <Topbar
          page={page} theme={theme}
          toggleTheme={() => setTheme(t => t === "dark" ? "light" : "dark")}
          onMenuClick={() => setSidebarOpen(o => !o)}
          onMobileMenu={() => setMobileSidebar(o => !o)}
        />
        <main className="app-content">
          {page === "home"      && <Landing   onStart={navigate} />}
          {page === "analyzer"  && <Analyzer  />}
          {page === "dashboard" && <Dashboard />}
          {page === "history"   && <History   />}
          {page === "about"     && <About     />}
        </main>
      </div>
      {mobileSidebar && <div className="sidebar-overlay" onClick={() => setMobileSidebar(false)} />}
    </div>
  );
}
