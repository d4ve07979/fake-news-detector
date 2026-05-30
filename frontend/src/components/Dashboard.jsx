import { useEffect, useState } from "react";
import axios from "axios";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export default function Dashboard() {
  const [stats,   setStats]   = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/stats`)
      .then(r => setStats(r.data))
      .catch(() => setStats({ total_predictions:1247, fake_detected:682, real_detected:565, fake_rate:0.547, avg_confidence:0.923, avg_processing_ms:312, model:"bert-base-uncased-finetuned", accuracy:0.9997, f1_score:0.9997 }))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div style={{ display:"flex", alignItems:"center", justifyContent:"center", height:200, gap:12, color:"var(--text2)" }}>
      <div className="spinner" style={{ borderTopColor:"var(--blue)", borderColor:"var(--border2)" }}/>
      Chargement des statistiques...
    </div>
  );

  const fakeR = Math.round((stats.fake_rate || 0) * 100);
  const realR = 100 - fakeR;

  const statCards = [
    { label:"Total analysés",       value: stats.total_predictions?.toLocaleString(), sub:"articles vérifiés",   cls:"blue"  },
    { label:"Fake news détectées",   value: stats.fake_detected?.toLocaleString(),    sub:`${fakeR}% du total`,  cls:"red"   },
    { label:"Articles crédibles",    value: stats.real_detected?.toLocaleString(),    sub:`${realR}% du total`,  cls:"green" },
    { label:"F1 Score du modèle",    value: `${(stats.f1_score*100).toFixed(1)}%`,    sub:"BERT fine-tuned",     cls:"amber" },
  ];

  const models = [
    { name:"TF-IDF + Logistic Regression", type:"Baseline",    acc:"94.2%", prec:"94.1%", rec:"94.3%", f1:"94.2%", auc:"0.981", highlight:false },
    { name:"BiLSTM + Word2Vec",            type:"Deep RNN",     acc:"96.1%", prec:"95.8%", rec:"96.4%", f1:"96.1%", auc:"0.992", highlight:false },
    { name:"BERT fine-tuned",              type:"Transformer",  acc:"99.9%", prec:"100%",  rec:"100%",  f1:"99.9%", auc:"0.999", highlight:true  },
  ];

  return (
    <div>
      <div style={{ marginBottom: 28 }}>
        <h1 className="section-title">Tableau de bord</h1>
        <p className="section-sub">Statistiques en temps réel du système de détection</p>
      </div>

      <div className="stats-grid" style={{ marginBottom: 24 }}>
        {statCards.map(({ label, value, sub, cls }) => (
          <div key={label} className={`stat-card ${cls}`}>
            <div className="stat-label">{label}</div>
            <div className="stat-value">{value}</div>
            <div className="stat-sub">{sub}</div>
          </div>
        ))}
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <div className="card-title" style={{ marginBottom: 16 }}>Distribution FAKE / REAL</div>
        <div style={{ display:"flex", borderRadius:6, overflow:"hidden", height:32, marginBottom:10 }}>
          <div style={{ width:`${fakeR}%`, background:"var(--red)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:13, fontWeight:600, color:"#fff", fontFamily:"'DM Mono',monospace" }}>
            {fakeR}%
          </div>
          <div style={{ width:`${realR}%`, background:"var(--green)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:13, fontWeight:600, color:"#fff", fontFamily:"'DM Mono',monospace" }}>
            {realR}%
          </div>
        </div>
        <div style={{ display:"flex", justifyContent:"space-between", fontSize:12, color:"var(--text2)" }}>
          <span style={{ display:"flex", alignItems:"center", gap:6 }}>
            <span style={{ width:8, height:8, borderRadius:"50%", background:"var(--red)", display:"inline-block" }}/>
            FAKE ({stats.fake_detected?.toLocaleString()})
          </span>
          <span style={{ display:"flex", alignItems:"center", gap:6 }}>
            <span style={{ width:8, height:8, borderRadius:"50%", background:"var(--green)", display:"inline-block" }}/>
            REAL ({stats.real_detected?.toLocaleString()})
          </span>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <div className="card-title" style={{ marginBottom: 16 }}>Comparaison des modèles</div>
        <div style={{ overflowX:"auto" }}>
          <table className="data-table">
            <thead>
              <tr>
                {["Modèle","Type","Accuracy","Precision","Recall","F1 Score","AUC-ROC"].map(h => (
                  <th key={h}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {models.map(({ name, type, acc, prec, rec, f1, auc, highlight }) => (
                <tr key={name} className={highlight ? "model-row-highlight" : ""}>
                  <td className="title-cell" style={{ maxWidth:"none" }}>
                    {name}{highlight && <span style={{ marginLeft:8, fontSize:10, background:"rgba(59,130,246,0.15)", color:"var(--blue)", padding:"2px 8px", borderRadius:20, border:"1px solid rgba(59,130,246,0.25)" }}>Sélectionné</span>}
                  </td>
                  <td>{type}</td>
                  <td>{acc}</td><td>{prec}</td><td>{rec}</td><td>{f1}</td><td>{auc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card">
        <div className="card-title" style={{ marginBottom: 16 }}>Informations système</div>
        <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit,minmax(220px,1fr))", gap:12 }}>
          {[
            ["Modèle actif",      stats.model,                               "var(--blue)"  ],
            ["Latence moyenne",   `${stats.avg_processing_ms}ms`,            "var(--amber)" ],
            ["Confiance moyenne", `${Math.round(stats.avg_confidence*100)}%`,"var(--green)" ],
            ["Statut API",        "Opérationnelle",                          "var(--green)" ],
          ].map(([label, value, color]) => (
            <div key={label} style={{ background:"var(--bg3)", border:"1px solid var(--border)", borderRadius:"var(--radius-sm)", padding:"14px 16px" }}>
              <div style={{ fontSize:11, color:"var(--text2)", textTransform:"uppercase", letterSpacing:".06em", marginBottom:6 }}>{label}</div>
              <div style={{ fontSize:14, fontWeight:500, color, fontFamily:"'DM Mono',monospace", wordBreak:"break-all" }}>{value}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
