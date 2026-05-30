"""Configuration settings"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MODEL_PATH: str = "./models/bert-fakenews"
    MODEL_VERSION: str = "1.0.0"
    DATABASE_URL: str = "postgresql://fakenews:password@db:5432/fakenews_db"
    DEBUG: bool = False
    class Config:
        env_file = ".env"

settings = Settings()
