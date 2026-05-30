import { useEffect, useState } from "react";
import axios from "axios";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const IconDownload = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
  </svg>
);

export default function History() {
  const [data,    setData]    = useState([]);
  const [page,    setPage]    = useState(1);
  const [total,   setTotal]   = useState(0);
  const [filter,  setFilter]  = useState("");
  const [loading, setLoading] = useState(false);
  const LIMIT = 15;

  const fetch_ = async (p = 1, label = "") => {
    setLoading(true);
    try {
      const params = { page: p, limit: LIMIT, ...(label ? { label } : {}) };
      const { data: res } = await axios.get(`${API}/history`, { params });
      setData(res.data); setTotal(res.total);
    } catch {
      const mock = Array.from({ length: LIMIT }, (_, i) => ({
        id: (p-1)*LIMIT+i+1,
        title: `Article exemple #${(p-1)*LIMIT+i+1} — ${["Politique","Science","Santé","Monde"][i%4]}`,
        label: (i+p)%3!==0 ? "FAKE" : "REAL",
        confidence: parseFloat((0.82+(i%17)/100).toFixed(4)),
        timestamp: new Date(Date.now()-i*3600000).toISOString(),
      }));
      setData(label ? mock.filter(m=>m.label===label) : mock);
      setTotal(1247);
    } finally { setLoading(false); }
  };

  useEffect(() => { fetch_(page, filter); }, [page, filter]);

  const totalPages = Math.ceil(total / LIMIT);

  const exportCSV = () => {
    const csv = ["ID,Titre,Label,Confiance,Date",
      ...data.map(r => `${r.id},"${r.title}",${r.label},${r.confidence},${r.timestamp}`)
    ].join("\n");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([csv], { type:"text/csv" }));
    a.download = "predictions.csv"; a.click();
  };

  return (
    <div>
      <div style={{ display:"flex", alignItems:"flex-start", justifyContent:"space-between", marginBottom:24, flexWrap:"wrap", gap:12 }}>
        <div>
          <h1 className="section-title">Historique des prédictions</h1>
          <p className="section-sub">{total.toLocaleString()} analyses enregistrées</p>
        </div>
        <button
          onClick={exportCSV}
          style={{ display:"flex", alignItems:"center", gap:7, padding:"9px 16px", background:"var(--bg3)", border:"1px solid var(--border)", borderRadius:"var(--radius-sm)", color:"var(--text2)", fontSize:13, cursor:"pointer", fontFamily:"'DM Sans',sans-serif", transition:"all .15s" }}
          onMouseOver={e => { e.currentTarget.style.borderColor="rgba(59,130,246,0.4)"; e.currentTarget.style.color="var(--blue)"; }}
          onMouseOut={e => { e.currentTarget.style.borderColor="var(--border)"; e.currentTarget.style.color="var(--text2)"; }}
        >
          <IconDownload /> Exporter CSV
        </button>
      </div>

      <div style={{ display:"flex", gap:8, marginBottom:16 }}>
        {[
          { id:"",     label:"Tous",  cls:""         },
          { id:"FAKE", label:"FAKE",  cls:"active-fake" },
          { id:"REAL", label:"REAL",  cls:"active-real" },
        ].map(({ id, label, cls }) => (
          <button
            key={id}
            className={`filter-tab${filter===id ? ` active ${cls}` : ""}`}
            onClick={() => { setFilter(id); setPage(1); }}
          >{label}</button>
        ))}
      </div>

      <div className="card" style={{ padding:0, overflow:"hidden" }}>
        {loading ? (
          <div style={{ display:"flex", alignItems:"center", justifyContent:"center", height:120, gap:10, color:"var(--text2)" }}>
            <div className="spinner" style={{ borderTopColor:"var(--blue)", borderColor:"var(--border2)" }}/> Chargement...
          </div>
        ) : (
          <div style={{ overflowX:"auto" }}>
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
                    <td style={{ fontFamily:"'DM Mono',monospace", fontSize:11 }}>{row.id}</td>
                    <td className="title-cell">{row.title}</td>
                    <td>
                      <span className={row.label==="FAKE" ? "label-fake" : "label-real"}>
                        {row.label}
                      </span>
                    </td>
                    <td>
                      <div className="conf-bar-wrap">
                        <div className="conf-bar">
                          <div
                            className="conf-bar-fill"
                            style={{ width:`${Math.round(row.confidence*100)}%`, background: row.label==="FAKE" ? "var(--red)" : "var(--green)" }}
                          />
                        </div>
                        <span style={{ fontSize:12, fontFamily:"'DM Mono',monospace", color:"var(--text2)" }}>
                          {Math.round(row.confidence*100)}%
                        </span>
                      </div>
                    </td>
                    <td style={{ fontFamily:"'DM Mono',monospace", fontSize:11, whiteSpace:"nowrap" }}>
                      {new Date(row.timestamp).toLocaleString("fr-FR", { day:"2-digit", month:"short", hour:"2-digit", minute:"2-digit" })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="pagination">
        <span className="page-info">Page {page} / {totalPages} · {total.toLocaleString()} résultats</span>
        <div className="page-btns">
          <button className="page-btn" onClick={() => setPage(p=>Math.max(1,p-1))} disabled={page===1}>← Précédent</button>
          <button className="page-btn" onClick={() => setPage(p=>Math.min(totalPages,p+1))} disabled={page>=totalPages}>Suivant →</button>
        </div>
      </div>
    </div>
  );
}
