import { useState } from "react";
import axios from "axios";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const IconShield = ({ ok }) => ok ? (
  <svg viewBox="0 0 24 24" fill="none" stroke="var(--green)" strokeWidth="2" strokeLinecap="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    <polyline points="9 12 11 14 15 10"/>
  </svg>
) : (
  <svg viewBox="0 0 24 24" fill="none" stroke="var(--red)" strokeWidth="2" strokeLinecap="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    <line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
  </svg>
);

const TEST_ARTICLES = [
  {
    label: "Vrai — Reuters",
    title: "Federal Reserve holds interest rates steady amid inflation concerns",
    text: "The Federal Reserve kept interest rates unchanged on Wednesday, as expected, while signaling it remains committed to bringing inflation down to its 2% target. Chair Jerome Powell said the committee would continue to monitor incoming data carefully before making any adjustments to monetary policy.",
  },
  {
    label: "Fake — Complotiste",
    title: "BREAKING: Secret Government Plan to Microchip Citizens Through Vaccines EXPOSED",
    text: "WAKE UP PEOPLE!!! A whistleblower from inside the deep state has leaked documents proving that COVID vaccines contain microchips designed to track every citizen on the planet. The mainstream media is HIDING this from you! Share before they DELETE this! They don't want you to know the TRUTH!!!",
  },
  {
    label: "Vrai — Science",
    title: "NASA Artemis mission successfully completes lunar orbit",
    text: "NASA Orion capsule successfully completed its closest approach to the Moon on Monday as part of the Artemis I mission. The uncrewed spacecraft came within 130 kilometers of the lunar surface. Mission controllers at Johnson Space Center reported all systems were performing nominally.",
  },
];

export default function Analyzer() {
  const [title,  setTitle]  = useState("");
  const [text,   setText]   = useState("");
  const [result, setResult] = useState(null);
  const [loading,setLoading]= useState(false);
  const [error,  setError]  = useState(null);

  const analyze = async () => {
    if (!title.trim() || text.trim().length < 10) {
      setError("Veuillez saisir un titre et un texte d'au moins 10 caractères.");
      return;
    }
    setLoading(true); setError(null); setResult(null);
    try {
      const { data } = await axios.post(`${API}/predict`, { title, text });
      setResult(data);
    } catch (e) {
      setError(e.response?.data?.detail || "Impossible de joindre l'API.");
    } finally { setLoading(false); }
  };

  const isFake  = result?.label === "FAKE";
  const fakePct = result ? Math.round((result.fake_probability || 0) * 100) : 0;
  const realPct = 100 - fakePct;
  const confPct = result ? Math.round((result.confidence || 0) * 100) : 0;

  return (
    <div style={{ maxWidth: 740, margin: "0 auto" }}>
      <div className="page-header">
        <h1 className="page-title">Analyser un article</h1>
        <p className="page-sub">Détection de fake news basée sur BERT fine-tuné · 44 898 articles d'entraînement</p>
      </div>

      <div className="card">
        <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
          <div>
            <label className="field-label">Titre de l'article</label>
            <input className="field" value={title} onChange={e=>setTitle(e.target.value)}
              placeholder="Ex: Scientists confirm major discovery in renewable energy" />
          </div>
          <div>
            <label className="field-label">Corps de l'article</label>
            <textarea className="field" rows={7} value={text} onChange={e=>setText(e.target.value)}
              placeholder="Collez ici le texte complet de l'article..." />
            <div className="field-meta">{text.length} car · {text.split(/\s+/).filter(Boolean).length} mots</div>
          </div>
          {error && <div className="error-box">{error}</div>}
          <button className="btn btn-primary" onClick={analyze} disabled={loading}>
            {loading
              ? <><div className="spinner" style={{borderTopColor:"#fff",borderColor:"rgba(255,255,255,.3)"}}/> Analyse en cours...</>
              : "Analyser l'article"}
          </button>
        </div>
      </div>

      {result && (
        <div className={`result-card ${isFake?"fake":"real"}`}>
          <div className="result-row">
            <div style={{display:"flex",gap:12,flex:1}}>
              <div className="result-icon"><IconShield ok={!isFake}/></div>
              <div>
                <div className="result-verdict">{isFake?"Fake News":"Information crédible"}</div>
                <div className="result-time">{result.processing_time_ms}ms · {new Date(result.timestamp).toLocaleString("fr-FR")}</div>
              </div>
            </div>
            <div className="result-score">
              <div className="score-big">{confPct}%</div>
              <div className="score-label">confiance</div>
            </div>
          </div>
          <div className="prob-track">
            <div className={`prob-fill ${isFake?"fake":"real"}`} style={{width:`${isFake?fakePct:realPct}%`}}/>
          </div>
          <div className="prob-labels">
            <span style={{color:"var(--green)"}}>REAL {realPct}%</span>
            <span style={{color:"var(--red)"}}>{fakePct}% FAKE</span>
          </div>
          {result.lang_warning==="fr" && (
            <div className="lang-warning" style={{marginTop:12}}>
              ⚠ Texte en français détecté — modèle entraîné sur l'anglais. Utilisez les articles de test ci-dessous pour de meilleurs résultats.
            </div>
          )}
          {result.top_keywords?.length>0 && (
            <div className="keywords-row" style={{marginTop:12}}>
              {result.top_keywords.map((kw,i)=><span key={i} className="kw">{kw}</span>)}
            </div>
          )}
        </div>
      )}

      <div className="card" style={{marginTop:16}}>
        <div className="card-header">
          <div>
            <div className="card-title">Articles de test (anglais)</div>
            <div className="card-sub">Cliquez pour charger et tester le modèle</div>
          </div>
        </div>
        <div style={{display:"flex",flexDirection:"column",gap:8}}>
          {TEST_ARTICLES.map(({label,title:t,text:tx})=>(
            <button key={label}
              onClick={()=>{setTitle(t);setText(tx);setResult(null);setError(null);}}
              style={{textAlign:"left",background:"var(--bg-input)",border:"1px solid var(--border)",borderRadius:"var(--radius-sm)",padding:"10px 14px",color:"var(--text-sec)",fontSize:13,cursor:"pointer",fontFamily:"'Inter',sans-serif",transition:"all .15s",display:"flex",alignItems:"center",gap:10}}
              onMouseOver={e=>e.currentTarget.style.borderColor="var(--accent)"}
              onMouseOut={e=>e.currentTarget.style.borderColor="var(--border)"}
            >
              <span style={{fontSize:10,padding:"2px 8px",borderRadius:10,background:"var(--bg-hover)",color:"var(--text-sec)",flexShrink:0}}>{label}</span>
              <span style={{overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{t}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
