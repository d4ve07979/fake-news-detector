"""
Database — SQLAlchemy
SQLite en développement, PostgreSQL en production (Docker)
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

# SQLite par défaut (dev), PostgreSQL si DATABASE_URL défini (Docker/prod)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./fakenews_dev.db"
)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine       = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base         = declarative_base()


class Prediction(Base):
    """Table des prédictions — une ligne par article analysé."""
    __tablename__ = "predictions"

    id           = Column(Integer,  primary_key=True, index=True, autoincrement=True)
    title        = Column(String(500))
    text_snippet = Column(String(300))
    source       = Column(String(100), nullable=True)
    label        = Column(String(10))       # "FAKE" ou "REAL"
    confidence   = Column(Float)
    fake_prob    = Column(Float)
    real_prob    = Column(Float)
    keywords     = Column(String(500), nullable=True)
    created_at   = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Crée les tables si elles n'existent pas encore."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Générateur de session — injecté automatiquement par FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
