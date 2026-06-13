import { useEffect, useState } from "react";
import axios from "axios";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const IconDownload = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="7 10 12 15 17 10"/>
    <line x1="12" y1="15" x2="12" y2="3"/>
  </svg>
);

export default function History() {
  const [data,    setData]    = useState([]);
  const [page,    setPage]    = useState(1);
  const [total,   setTotal]   = useState(0);
  const [filter,  setFilter]  = useState("");
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);
  const LIMIT = 15;

  const fetchHistory = async (p = 1, label = "") => {
    setLoading(true);
    setError(null);
    try {
      const params = { page: p, limit: LIMIT, ...(label ? { label } : {}) };
      const { data: res } = await axios.get(`${API}/history`, { params });
      setData(res.data || []);
      setTotal(res.total || 0);
    } catch (e) {
      // Afficher l'erreur réelle — ne plus masquer avec des données mockées
      setError("Impossible de charger l'historique. Vérifiez que le backend tourne.");
      setData([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory(page, filter);
  }, [page, filter]);

  const totalPages = Math.max(1, Math.ceil(total / LIMIT));

  const exportCSV = () => {
    if (data.length === 0) return;
    const csv = [
      "ID,Titre,Label,Confiance,Source,Date",
      ...data.map(r =>
        `${r.id},"${(r.title || "").replace(/"/g, '""')}",${r.label},${r.confidence},"${r.source || ""}",${r.timestamp}`
      ),
    ].join("\n");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8;" }));
    a.download = `predictions_${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
  };

  return (
    <div>
      {/* ── En-tête ──────────────────────────────────────── */}
      <div style={{ display:"flex", alignItems:"flex-start", justifyContent:"space-between", marginBottom:24, flexWrap:"wrap", gap:12 }}>
        <div className="page-header" style={{ marginBottom:0 }}>
          <h1 className="page-title">Historique des prédictions</h1>
          <p className="page-sub">
            {total > 0
              ? `${total.toLocaleString()} analyses enregistrées en base de données`
              : "Aucune analyse enregistrée pour le moment"}
          </p>
        </div>
        <button
          onClick={exportCSV}
          disabled={data.length === 0}
          className="btn btn-ghost"
          style={{ display:"flex", alignItems:"center", gap:7 }}
        >
          <IconDownload /> Exporter CSV
        </button>
      </div>

      {/* ── Filtres ───────────────────────────────────────── */}
      <div className="tab-group" style={{ marginBottom:16 }}>
        {[
          { id:"",     label:"Tous" },
          { id:"FAKE", label:"FAKE" },
          { id:"REAL", label:"REAL" },
        ].map(({ id, label }) => (
          <button
            key={id}
            className={[
              "tab",
              filter === id ? "active" : "",
              filter === id && id === "FAKE" ? "fake-tab" : "",
              filter === id && id === "REAL" ? "real-tab" : "",
            ].filter(Boolean).join(" ")}
            onClick={() => { setFilter(id); setPage(1); }}
          >
            {label}
          </button>
        ))}
      </div>

      {/* ── Tableau ───────────────────────────────────────── */}
      <div className="card" style={{ padding:0, overflow:"hidden" }}>
        {loading ? (
          <div style={{ display:"flex", alignItems:"center", justifyContent:"center", height:140, gap:10, color:"var(--text-sec)" }}>
            <div className="spinner" /> Chargement...
          </div>

        ) : error ? (
          <div style={{ padding:24 }}>
            <div className="error-box">{error}</div>
            <button
              className="btn btn-ghost"
              style={{ marginTop:12 }}
              onClick={() => fetchHistory(page, filter)}
            >
              Réessayer
            </button>
          </div>

        ) : data.length === 0 ? (
          <div style={{ padding:40, textAlign:"center", color:"var(--text-sec)" }}>
            <div style={{ fontSize:32, marginBottom:12 }}>📋</div>
            <div style={{ fontSize:14, fontWeight:500, marginBottom:6 }}>
              {filter ? `Aucun article "${filter}" dans l'historique` : "Aucune analyse enregistrée"}
            </div>
            <div style={{ fontSize:13, color:"var(--text-ter)" }}>
              Analysez des articles depuis la page "Analyser" pour les voir apparaître ici.
            </div>
          </div>

        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ width:50 }}>#</th>
                  <th>Titre</th>
                  <th>Label</th>
                  <th>Confiance</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {data.map(row => (
                  <tr key={row.id}>
                    <td style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:11, color:"var(--text-ter)" }}>
                      {row.id}
                    </td>
                    <td className="text-pri" style={{ maxWidth:280, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>
                      {row.title || "—"}
                    </td>
                    <td>
                      <span className={row.label === "FAKE" ? "pill pill-fake" : "pill pill-real"}>
                        {row.label}
                      </span>
                    </td>
                    <td>
                      <div style={{ display:"flex", alignItems:"center", gap:8 }}>
                        <div style={{ width:72, height:4, background:"var(--bg-input)", borderRadius:2, overflow:"hidden", flexShrink:0 }}>
                          <div style={{
                            height:"100%", borderRadius:2,
                            width: `${Math.round((row.confidence || 0) * 100)}%`,
                            background: row.label === "FAKE"
                              ? "linear-gradient(90deg,#f43f5e,#fb7185)"
                              : "linear-gradient(90deg,#10b981,#34d399)",
                          }}/>
                        </div>
                        <span style={{ fontSize:12, fontFamily:"'JetBrains Mono',monospace", color:"var(--text-sec)", flexShrink:0 }}>
                          {Math.round((row.confidence || 0) * 100)}%
                        </span>
                      </div>
                    </td>
                    <td style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:11, whiteSpace:"nowrap", color:"var(--text-sec)" }}>
                      {row.timestamp
                        ? new Date(row.timestamp).toLocaleString("fr-FR", {
                            day:"2-digit", month:"short",
                            hour:"2-digit", minute:"2-digit",
                          })
                        : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── Pagination ────────────────────────────────────── */}
      {total > 0 && (
        <div className="pagination">
          <span className="page-info">
            Page {page} / {totalPages} · {total.toLocaleString()} résultats
          </span>
          <div className="page-btns">
            <button
              className="page-btn"
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              ← Précédent
            </button>
            <button
              className="page-btn"
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
            >
              Suivant →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
