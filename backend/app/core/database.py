"""Database — SQLAlchemy + PostgreSQL"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Prediction(Base):
    __tablename__ = "predictions"
    id           = Column(Integer, primary_key=True, index=True)
    title        = Column(String(500))
    text_snippet = Column(String(300))
    source       = Column(String(100), nullable=True)
    label        = Column(String(10))  # FAKE or REAL
    confidence   = Column(Float)
    fake_prob    = Column(Float)
    real_prob    = Column(Float)
    keywords     = Column(String(500), nullable=True)
    created_at   = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
