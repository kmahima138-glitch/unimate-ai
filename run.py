#!/usr/bin/env python3
import os
import sys
import uvicorn
from pathlib import Path

# Set project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.config import settings
from backend.app.db.database import db

def main():
    print("=" * 60)
    print("  🎓 UNIMATE AI — Intelligent University Assistant (RAG)")
    print("=" * 60)
    print(f"  * Mode: {'Production' if settings.APP_ENV == 'production' else 'Development'}")
    print(f"  * Database: {settings.DB_URL}")
    print(f"  * Gemini Model: {settings.GEMINI_MODEL}")
    print(f"  * Gemini API Key: {'Configured ✅' if settings.GEMINI_API_KEY else 'Offline Grounded Mode ⚡'}")
    print(f"  * Web Portal: http://localhost:{settings.PORT}")
    print(f"  * API Docs: http://localhost:{settings.PORT}/docs")
    print("=" * 60)

    # Initialize database
    db.init_db()

    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False
    )

if __name__ == "__main__":
    main()
