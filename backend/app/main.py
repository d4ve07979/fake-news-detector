"""
Fake News Detector — FastAPI Backend
Projet IA & Big Data L3 — KENKOU Dave et al.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
import uvicorn
import logging

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.database import engine, Base
from app.services.model_service import ModelService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Global model instance ──────────────────────────────────────────────────
model_service: ModelService = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup, cleanup on shutdown."""
    global model_service
    logger.info(" Loading BERT model...")
    model_service = ModelService()
    model_service.load_model(settings.MODEL_PATH)
    logger.info(" Model loaded successfully.")
    app.state.model_service = model_service
    yield
    logger.info(" Shutting down...")

# ── App factory ────────────────────────────────────────────────────────────
app = FastAPI(
    title="Fake News Detector API",
    description="API de détection de fake news basée sur BERT — Projet L3 IA & Big Data",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "model_loaded": model_service is not None and model_service.is_loaded,
        "model_version": settings.MODEL_VERSION,
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
