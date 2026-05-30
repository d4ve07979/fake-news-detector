import { useEffect, useState } from "react";
import axios from "axios";

const API = "http://localhost:8000";

const features = [
  { icon:<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>, title:"BERT Fine-tuned", desc:"Transformer entraîné sur 44 898 articles · F1 = 99.9%", color:"#6366f1" },
  { icon:<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>, title:"Temps réel", desc:"Analyse complète en moins de 500ms via FastAPI", color:"#a855f7" },
  { icon:<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><ellipse cx="12" cy="12" rx="10" ry="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>, title:"Multilingue", desc:"XLM-RoBERTa · support EN, FR et 100+ langues", color:"#ec4899" },
  { icon:<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>, title:"Pipeline Spark", desc:"Prétraitement Big Data distribué Apache Spark NLP", color:"#f59e0b" },
];

const pipeline = [
  { step:"CSV", sub:"Raw data",  color:"#6366f1" },
  { step:"Spark",sub:"NLP clean",color:"#a855f7" },
  { step:"Parquet",sub:"Big Data",color:"#ec4899"},
  { step:"BERT", sub:"Training", color:"#f43f5e" },
  { step:"API",  sub:"FastAPI",  color:"#f59e0b" },
  { step:"App",  sub:"React",    color:"#10b981" },
];

export default function Landing({ onStart }) {
  const [apiOk, setApiOk] = useState(null);

  useEffect(() => {
    axios.get(`${API}/health`, { timeout:3000 })
      .then(r => setApiOk(r.data.model_loaded))
      .catch(() => setApiOk(false));
  }, []);

  return (
    <div style={{ maxWidth:860, margin:"0 auto" }}>

      {/* ── Hero ─────────────────────────────────────── */}
      <div style={{ textAlign:"center", padding:"52px 0 44px" }}>
        <div style={{ display:"inline-flex", alignItems:"center", gap:8, background:"rgba(99,102,241,0.12)", border:"1px solid rgba(99,102,241,0.3)", borderRadius:20, padding:"6px 16px", marginBottom:24 }}>
          <div style={{ width:7, height:7, borderRadius:"50%", background: apiOk ? "#10b981" : "#6366f1", boxShadow: apiOk ? "0 0 8px #10b981" : "none" }}/>
          <span style={{ fontSize:12, color:"#818cf8", fontWeight:600 }}>
            {apiOk === null ? "Connexion..." : apiOk ? "Système opérationnel" : "Mode démo"}
            {" · "}Projet L3 IA &amp; Big Data
          </span>
        </div>

        <h1 style={{ fontSize:"clamp(30px,5.5vw,54px)", fontWeight:800, lineHeight:1.1, marginBottom:10, letterSpacing:"-.03em", color:"var(--text-pri)" }}>
          Détection de
        </h1>
        <h1 style={{ fontSize:"clamp(30px,5.5vw,54px)", fontWeight:800, lineHeight:1.1, marginBottom:20, letterSpacing:"-.03em" }}
          className="grad-text">
          Fake News
        </h1>
        <h2 style={{ fontSize:"clamp(30px,5.5vw,54px)", fontWeight:800, lineHeight:1.1, marginBottom:24, letterSpacing:"-.03em", color:"var(--text-pri)" }}>
          à grande échelle
        </h2>

        <p style={{ fontSize:15, color:"var(--text-sec)", maxWidth:520, margin:"0 auto 36px", lineHeight:1.8 }}>
          Système complet basé sur BERT Transformer, pipeline Apache Spark
          et API FastAPI — conçu pour analyser des millions d'articles en temps réel.
        </p>

        <div style={{ display:"flex", gap:12, justifyContent:"center", flexWrap:"wrap" }}>
          <button onClick={() => onStart("analyzer")} className="btn btn-primary"
            style={{ width:"auto", padding:"13px 32px", fontSize:14, borderRadius:50 }}>
            Analyser un article →
          </button>
          <button onClick={() => onStart("dashboard")} className="btn btn-ghost"
            style={{ padding:"13px 32px", fontSize:14, borderRadius:50 }}>
            Voir le dashboard
          </button>
        </div>
      </div>

      {/* ── Stats row ───────────────────────────────── */}
      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit,minmax(140px,1fr))", gap:10, marginBottom:28 }}>
        {[
          { v:"44 898",  l:"Articles d'entraînement" },
          { v:"99.9%",   l:"F1 Score test set"       },
          { v:"<500ms",  l:"Temps réponse API"        },
          { v:"3",       l:"Modèles comparés"         },
        ].map(({ v, l }) => (
          <div key={l} style={{ background:"var(--bg-card)", border:"1px solid var(--border)", borderRadius:"var(--radius)", padding:"16px", textAlign:"center" }}>
            <div style={{ fontSize:24, fontWeight:800, fontFamily:"'JetBrains Mono',monospace", letterSpacing:"-.02em" }} className="grad-text">{v}</div>
            <div style={{ fontSize:11, color:"var(--text-sec)", marginTop:5, textTransform:"uppercase", letterSpacing:".06em" }}>{l}</div>
          </div>
        ))}
      </div>

      {/* ── Features ─────────────────────────────────── */}
      <div className="card" style={{ marginBottom:16 }}>
        <div className="card-header"><div className="card-title">Fonctionnalités principales</div></div>
        <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit,minmax(230px,1fr))", gap:12 }}>
          {features.map(({ icon, title, desc, color }) => (
            <div key={title} style={{ display:"flex", gap:14, padding:"14px 16px", borderRadius:"var(--radius-sm)", background:"var(--bg-input)", border:"1px solid var(--border)", transition:"border-color .18s" }}
              onMouseOver={e=>e.currentTarget.style.borderColor=color+"55"}
              onMouseOut={e=>e.currentTarget.style.borderColor="var(--border)"}
            >
              <div style={{ color, flexShrink:0, marginTop:1 }}>{icon}</div>
              <div>
                <div style={{ fontWeight:700, fontSize:13.5, marginBottom:4, color:"var(--text-pri)" }}>{title}</div>
                <div style={{ fontSize:12, color:"var(--text-sec)", lineHeight:1.6 }}>{desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Pipeline ─────────────────────────────────── */}
      <div className="card">
        <div className="card-title" style={{ marginBottom:16 }}>Pipeline de données bout en bout</div>
        <div style={{ display:"flex", alignItems:"center", overflowX:"auto", padding:"4px 0", gap:0 }}>
          {pipeline.map(({ step, sub, color }, i, arr) => (
            <div key={step} style={{ display:"flex", alignItems:"center", flexShrink:0 }}>
              <div style={{ textAlign:"center", minWidth:80 }}>
                <div style={{ background:`${color}12`, border:`1px solid ${color}35`, borderRadius:"var(--radius-sm)", padding:"10px 8px" }}>
                  <div style={{ fontSize:12.5, fontWeight:700, color }}>{step}</div>
                  <div style={{ fontSize:10, color:"var(--text-sec)", marginTop:2 }}>{sub}</div>
                </div>
              </div>
              {i < arr.length-1 && <div style={{ color:"var(--text-ter)", fontSize:18, margin:"0 2px", flexShrink:0 }}>→</div>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
