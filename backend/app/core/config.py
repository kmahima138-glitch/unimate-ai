import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "UniMate AI"
    APP_ENV: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["*"]

    # Google Gemini LLM API
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Storage paths
    DATA_DIR: str = str(BASE_DIR / "data")
    DB_URL: str = f"sqlite:///{BASE_DIR / 'data' / 'unimate.db'}"
    UPLOAD_DIR: str = str(BASE_DIR / "data" / "uploads")
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / "data" / "chromadb")

    # Document RAG parameters
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 100
    TOP_K_RETRIEVAL: int = 4
    SIMILARITY_THRESHOLD: float = 0.25

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure critical data directories exist
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
