"""Schémas Pydantic pour les prédictions"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PredictionCreate(BaseModel):
    title: str
    text: str
    source: Optional[str] = None

class PredictionResponse(BaseModel):
    id: int
    title: str
    label: str
    confidence: float
    fake_prob: float
    real_prob: float
    created_at: datetime

    class Config:
        from_attributes = True
