const team = [
  { initials:"KD", name:"KENKOU Dave", role:"Data Engineer", color:"#6366f1", tasks:["Pipeline Apache Spark NLP","EDA & prétraitement données","Architecture Big Data","Documentation technique"] },
  { initials:"M2", name:"Membre 2",    role:"ML Engineer",   color:"#a855f7", tasks:["Fine-tuning BERT sur GPU","Comparaison des modèles","Évaluation et métriques","Tests anti-overfitting"] },
  { initials:"M3", name:"Membre 3",    role:"Full-Stack Dev", color:"#10b981", tasks:["API FastAPI REST","Application React","Base de données","Déploiement Docker"] },
];
const metrics = [
  { label:"Accuracy",  value:"99.9%", bar:0.999 },
  { label:"F1 Score",  value:"99.9%", bar:0.999 },
  { label:"Precision", value:"100%",  bar:1.000 },
  { label:"Recall",    value:"100%",  bar:1.000 },
  { label:"AUC-ROC",   value:"0.999", bar:0.999 },
];
const timeline = [
  { week:"Semaine 1", title:"Data Engineering",  desc:"EDA complète sur 44 898 articles, pipeline Spark NLP, génération des fichiers Parquet stratifiés (70/15/15).", color:"#6366f1" },
  { week:"Semaine 2", title:"ML & Modélisation", desc:"Fine-tuning BERT sur Google Colab GPU T4, comparaison TF-IDF / BiLSTM / BERT, F1 = 99.9% sur test set.", color:"#a855f7" },
  { week:"Semaine 3", title:"App & Déploiement", desc:"API FastAPI, interface React avec sidebar, thème dark/light, conteneurisation Docker 4 services.", color:"#10b981" },
];

export default function About() {
  return (
    <div style={{ maxWidth:860, margin:"0 auto" }}>
      <div className="page-header">
        <h1 className="page-title">À propos du projet</h1>
        <p className="page-sub">Détection de Fake News à Grande Échelle — L3 Informatique, Spécialité IA &amp; Big Data · 2024/2025</p>
      </div>

      <div className="card" style={{ marginBottom:16 }}>
        <div className="card-title" style={{ marginBottom:12 }}>Contexte</div>
        <p style={{ fontSize:14, color:"var(--text-sec)", lineHeight:1.85 }}>
          Ce projet combine <strong style={{color:"var(--text-pri)"}}>Big Data Engineering</strong> (Apache Spark NLP) et <strong style={{color:"var(--text-pri)"}}>NLP de pointe</strong> (BERT Transformer) pour détecter automatiquement les fake news à grande échelle. Le dataset Kaggle de 44 898 articles (Reuters + sites de fake news) a été nettoyé via un pipeline Spark distribué avant le fine-tuning du modèle sur GPU.
        </p>
      </div>

      <div className="card" style={{ marginBottom:16 }}>
        <div className="card-title" style={{ marginBottom:16 }}>Performances du modèle BERT</div>
        <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
          {metrics.map(({ label, value, bar }) => (
            <div key={label}>
              <div style={{ display:"flex", justifyContent:"space-between", fontSize:13, marginBottom:6 }}>
                <span style={{ color:"var(--text-sec)", fontWeight:500 }}>{label}</span>
                <span style={{ fontFamily:"'JetBrains Mono',monospace", fontWeight:700, color:"var(--green)" }}>{value}</span>
              </div>
              <div style={{ height:6, background:"var(--bg-input)", borderRadius:3, overflow:"hidden" }}>
                <div style={{ height:"100%", width:`${bar*100}%`, background:"linear-gradient(90deg,#10b981,#34d399)", borderRadius:3 }}/>
              </div>
            </div>
          ))}
        </div>
        <div style={{ fontSize:12, color:"var(--text-sec)", marginTop:14, padding:"10px 14px", background:"var(--bg-input)", borderRadius:"var(--radius-sm)", borderLeft:"3px solid var(--amber)" }}>
          ⚠ Sur de nouveaux articles hors-dataset, accuracy ≈ 78% (biais de source Reuters). Correction en cours avec label smoothing et suppression des préfixes agences dans train_bert_v2.py.
        </div>
      </div>

      <div className="card" style={{ marginBottom:16 }}>
        <div className="card-title" style={{ marginBottom:16 }}>Équipe</div>
        <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit,minmax(220px,1fr))", gap:12 }}>
          {team.map(({ initials, name, role, color, tasks }) => (
            <div key={name} style={{ background:"var(--bg-input)", border:"1px solid var(--border)", borderRadius:"var(--radius)", padding:"18px", borderTop:`3px solid ${color}` }}>
              <div style={{ display:"flex", alignItems:"center", gap:12, marginBottom:14 }}>
                <div style={{ width:40, height:40, borderRadius:"50%", background:`${color}20`, display:"flex", alignItems:"center", justifyContent:"center", fontWeight:800, fontSize:13, color, flexShrink:0 }}>{initials}</div>
                <div>
                  <div style={{ fontWeight:700, fontSize:14, color:"var(--text-pri)" }}>{name}</div>
                  <div style={{ fontSize:11, color, fontWeight:600, textTransform:"uppercase", letterSpacing:".05em" }}>{role}</div>
                </div>
              </div>
              {tasks.map(t => (
                <div key={t} style={{ display:"flex", alignItems:"center", gap:8, fontSize:12.5, color:"var(--text-sec)", marginBottom:6 }}>
                  <div style={{ width:5, height:5, borderRadius:"50%", background:color, flexShrink:0 }}/>
                  {t}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="card-title" style={{ marginBottom:18 }}>Chronogramme</div>
        {timeline.map(({ week, title, desc, color }, i) => (
          <div key={week} style={{ display:"flex", gap:16, paddingBottom: i < timeline.length-1 ? 22 : 0 }}>
            <div style={{ display:"flex", flexDirection:"column", alignItems:"center", flexShrink:0 }}>
              <div style={{ width:12, height:12, borderRadius:"50%", background:color, marginTop:3, flexShrink:0, boxShadow:`0 0 8px ${color}` }}/>
              {i < timeline.length-1 && <div style={{ width:2, flex:1, background:"var(--border)", margin:"6px 0" }}/>}
            </div>
            <div>
              <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:5 }}>
                <span style={{ fontSize:11, fontWeight:700, color, textTransform:"uppercase", letterSpacing:".07em" }}>{week}</span>
                <span style={{ fontSize:14, fontWeight:700, color:"var(--text-pri)" }}>{title}</span>
              </div>
              <p style={{ fontSize:13, color:"var(--text-sec)", lineHeight:1.7 }}>{desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
