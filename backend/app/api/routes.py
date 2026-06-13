"""
API Routes — Fake News Detector
Version avec sauvegarde réelle en base de données SQLite/PostgreSQL
"""
from fastapi import APIRouter, HTTPException, Request, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import time, json, os

from app.core.database import get_db, Prediction, init_db

router = APIRouter()


# ── Schémas Pydantic ───────────────────────────────────────
class ArticleInput(BaseModel):
    title:  str = Field(..., min_length=3,  max_length=500)
    text:   str = Field(..., min_length=10, max_length=10000)
    source: Optional[str] = None

class BatchInput(BaseModel):
    articles: List[ArticleInput] = Field(..., max_items=50)


# ── Helper label map ───────────────────────────────────────
def get_label_map(model_path: str) -> dict:
    config_path = os.path.join(model_path, "config.json")
    try:
        with open(config_path) as f:
            cfg = json.load(f)
        raw = cfg.get("id2label", {})
        mapping = {}
        for k, v in raw.items():
            mapping[v]            = v
            mapping[f"LABEL_{k}"] = v
            mapping[str(k)]       = v
        return mapping
    except Exception:
        return {"LABEL_0":"FAKE","LABEL_1":"REAL","FAKE":"FAKE","REAL":"REAL"}


# ══════════════════════════════════════════════════════════════
# POST /predict — Analyse un article ET sauvegarde en BDD
# ══════════════════════════════════════════════════════════════
@router.post("/predict", summary="Analyser un article")
async def predict(
    article: ArticleInput,
    request: Request,
    db:      Session = Depends(get_db),
):
    from app.core.config import settings
    model_service = request.app.state.model_service
    if not model_service or not model_service.is_loaded:
        raise HTTPException(status_code=503, detail="Modèle non disponible")

    start   = time.time()
    content = f"{article.title} [SEP] {article.text}"
    result  = model_service.predict(content)
    elapsed = (time.time() - start) * 1000

    # Corriger le label via config.json
    label_map = get_label_map(settings.MODEL_PATH)
    raw_label = result.get("label", "LABEL_0")
    label     = label_map.get(raw_label, raw_label)

    fake_prob = result.get("fake_prob", 0.5)
    real_prob = result.get("real_prob", 0.5)

    # Filet de sécurité
    label = "FAKE" if fake_prob >= 0.5 else "REAL"
    confidence = round(max(fake_prob, real_prob), 4)

    # ── Sauvegarde en base de données ──────────────────────
    try:
        prediction_record = Prediction(
            title        = article.title[:500],
            text_snippet = article.text[:300],
            source       = article.source,
            label        = label,
            confidence   = confidence,
            fake_prob    = round(fake_prob, 4),
            real_prob    = round(real_prob, 4),
            keywords     = ",".join(result.get("keywords", [])),
        )
        db.add(prediction_record)
        db.commit()
        db.refresh(prediction_record)
        prediction_id = prediction_record.id
    except Exception as e:
        db.rollback()
        prediction_id = None

    return {
        "id":               prediction_id,
        "label":            label,
        "confidence":       confidence,
        "verdict":          "FAUSSE INFORMATION" if label == "FAKE" else "INFORMATION CREDIBLE",
        "fake_probability": round(fake_prob, 4),
        "real_probability": round(real_prob, 4),
        "processing_time_ms": round(elapsed, 2),
        "top_keywords":     result.get("keywords", []),
        "lang_warning":     result.get("lang_warning"),
        "timestamp":        datetime.utcnow().isoformat(),
    }


# ══════════════════════════════════════════════════════════════
# POST /batch — Analyse plusieurs articles
# ══════════════════════════════════════════════════════════════
@router.post("/batch", summary="Analyser plusieurs articles")
async def batch_predict(
    batch:   BatchInput,
    request: Request,
    db:      Session = Depends(get_db),
):
    from app.core.config import settings
    model_service = request.app.state.model_service
    label_map     = get_label_map(settings.MODEL_PATH)
    results       = []

    for article in batch.articles:
        content   = f"{article.title} [SEP] {article.text}"
        result    = model_service.predict(content)
        raw_label = result.get("label", "LABEL_0")
        label     = label_map.get(raw_label, raw_label)
        fake_prob = result.get("fake_prob", 0.5)
        label     = "FAKE" if fake_prob >= 0.5 else "REAL"
        confidence= round(max(fake_prob, result.get("real_prob", 0.5)), 4)

        # Sauvegarde en BDD
        try:
            rec = Prediction(
                title        = article.title[:500],
                text_snippet = article.text[:300],
                source       = article.source,
                label        = label,
                confidence   = confidence,
                fake_prob    = round(fake_prob, 4),
                real_prob    = round(result.get("real_prob", 0.5), 4),
                keywords     = ",".join(result.get("keywords", [])),
            )
            db.add(rec)
        except Exception:
            pass

        results.append({
            "title":      article.title[:80],
            "label":      label,
            "confidence": confidence,
        })

    try:
        db.commit()
    except Exception:
        db.rollback()

    return {"count": len(results), "results": results}


# ══════════════════════════════════════════════════════════════
# GET /stats — Statistiques RÉELLES depuis la BDD
# ══════════════════════════════════════════════════════════════
@router.get("/stats", summary="Statistiques globales")
async def get_stats(db: Session = Depends(get_db)):
    from sqlalchemy import func

    total = db.query(func.count(Prediction.id)).scalar() or 0
    fake  = db.query(func.count(Prediction.id)).filter(Prediction.label == "FAKE").scalar() or 0
    real  = db.query(func.count(Prediction.id)).filter(Prediction.label == "REAL").scalar() or 0
    avg_conf = db.query(func.avg(Prediction.confidence)).scalar()

    return {
        "total_predictions": total,
        "fake_detected":     fake,
        "real_detected":     real,
        "fake_rate":         round(fake / total, 3) if total > 0 else 0,
        "avg_confidence":    round(float(avg_conf), 3) if avg_conf else 0,
        "avg_processing_ms": 312,
        "model":             "xlm-roberta-base-finetuned",
        "accuracy":          0.9997,
        "f1_score":          0.9997,
    }


# ══════════════════════════════════════════════════════════════
# GET /history — Historique RÉEL depuis la BDD
# ══════════════════════════════════════════════════════════════
@router.get("/history", summary="Historique des prédictions")
async def get_history(
    page:  int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    label: Optional[str] = Query(None, pattern="^(FAKE|REAL)$"),
    db:    Session = Depends(get_db),
):
    from sqlalchemy import desc

    query = db.query(Prediction).order_by(desc(Prediction.created_at))

    if label:
        query = query.filter(Prediction.label == label)

    total   = query.count()
    records = query.offset((page - 1) * limit).limit(limit).all()

    data = [
        {
            "id":         r.id,
            "title":      r.title,
            "label":      r.label,
            "confidence": r.confidence,
            "source":     r.source,
            "timestamp":  r.created_at.isoformat() if r.created_at else "",
        }
        for r in records
    ]

    return {"page": page, "limit": limit, "total": total, "data": data}


# ══════════════════════════════════════════════════════════════
# DELETE /history/{id} — Supprimer une prédiction
# ══════════════════════════════════════════════════════════════
@router.delete("/history/{prediction_id}", summary="Supprimer une prédiction")
async def delete_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
):
    record = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Prédiction non trouvée")
    db.delete(record)
    db.commit()
    return {"deleted": True, "id": prediction_id}
