import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.core.config import settings
from backend.app.db.database import db
from backend.app.api.chat import router as chat_router
from backend.app.api.documents import router as documents_router
from backend.app.api.notices import router as notices_router
from backend.app.api.study import router as study_router
from backend.app.api.analytics import router as analytics_router

app = FastAPI(
    title=settings.APP_NAME,
    description="UniMate AI — Intelligent University Assistant powered by Retrieval-Augmented Generation (RAG)",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(notices_router)
app.include_router(study_router)
app.include_router(analytics_router)

# Mount uploads directory for document previews
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Frontend directory
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")

@app.on_event("startup")
def on_startup():
    db.init_db()
    # Auto-seed sample university knowledge base if database is empty
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM documents")
            if cursor.fetchone()["count"] == 0:
                print("Initializing and seeding sample knowledge base...")
                from backend.scripts.generate_sample_docs import (
                    create_sample_academic_regulations,
                    create_sample_exam_notice,
                    create_sample_docx
                )
                create_sample_academic_regulations()
                create_sample_exam_notice()
                create_sample_docx()
                from backend.scripts.seed_knowledge_base import seed
                seed()
    except Exception as e:
        print("Startup knowledge base initialization note:", e)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "llm_model": settings.GEMINI_MODEL,
        "has_api_key": bool(settings.GEMINI_API_KEY)
    }

# Serve Frontend SPA
@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    # If file exists in frontend, serve it
    file_path = os.path.join(FRONTEND_DIR, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    # Default to index.html
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "UniMate AI Backend API is running. Access endpoints under /api"}
