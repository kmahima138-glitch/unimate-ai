import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from backend.app.core.config import settings
from backend.app.schemas.document import DocumentResponse, DocumentUploadResponse, DocumentStatsResponse
from backend.app.services.document_ingestion import document_ingestion_service
from backend.app.services.notice_service import notice_service
from backend.app.db.database import db

router = APIRouter(prefix="/api/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    category: Optional[str] = Form("general")
):
    """
    Admin document upload endpoint.
    Accepts PDF or DOCX, extracts text page-by-page, generates chunks & embeddings,
    and indexes into the vector database with full source metadata.
    """
    filename = file.filename or "uploaded_document"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Only PDF (.pdf) and Word (.docx) documents are supported."
        )

    # Read file content and check size (25MB limit)
    contents = await file.read()
    file_size = len(contents)
    if file_size > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds the 25MB limit.")
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    doc_title = title.strip() if title and title.strip() else os.path.splitext(filename)[0].replace("_", " ").title()

    # Create pending document record
    doc_id = document_ingestion_service.create_pending_document(
        filename=filename,
        title=doc_title,
        category=category or "general",
        file_type=ext.replace(".", "").upper(),
        file_size=file_size,
        uploaded_by="admin"
    )

    # Save to disk
    save_path = os.path.join(settings.UPLOAD_DIR, f"{doc_id}_{filename}")
    with open(save_path, "wb") as f:
        f.write(contents)

    # Process ingestion synchronously to ensure immediate vector availability for testing
    try:
        result = document_ingestion_service.process_document(doc_id, save_path, category or "general")
        
        # If document is a notice or circular, auto-publish notice
        if category in ["examination", "fees", "scholarship", "events"] or "notice" in filename.lower() or "circular" in filename.lower():
            try:
                # Read first page text from chunks for notice extraction
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT text FROM document_chunks WHERE document_id = ? ORDER BY chunk_index ASC LIMIT 3", (doc_id,))
                    rows = cursor.fetchall()
                    combined_notice_text = " ".join([r["text"] for r in rows])
                    if combined_notice_text:
                        notice_service.extract_and_publish_notice(
                            title=doc_title,
                            content=combined_notice_text,
                            document_id=doc_id,
                            category=category
                        )
            except Exception:
                pass

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document indexing failed: {str(e)}")

    # Fetch updated record
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        doc_record = cursor.fetchone()

    return {
        "document": dict(doc_record),
        "message": f"Document '{doc_title}' successfully indexed with {result['chunk_count']} chunks."
    }

@router.get("", response_model=List[DocumentResponse])
def list_documents():
    """Lists all uploaded documents with processing status and chunk statistics."""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents ORDER BY uploaded_at DESC")
        return [dict(r) for r in cursor.fetchall()]

@router.get("/{document_id}/chunks")
def get_document_chunks(document_id: str):
    """Inspects indexed chunks for a document, showing chunk boundaries and page numbers."""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, document_id, chunk_index, page_number, text, metadata_json 
        FROM document_chunks 
        WHERE document_id = ? 
        ORDER BY chunk_index ASC
        """, (document_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

@router.delete("/{document_id}")
def delete_document(document_id: str):
    """Deletes a document from storage and purges all its chunks from the vector store."""
    success = document_ingestion_service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"message": "Document and associated vector chunks deleted successfully."}

@router.get("/stats/summary", response_model=DocumentStatsResponse)
def get_document_stats():
    """Returns knowledge-base statistics: document count, chunk count, and categories."""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM documents")
        total_docs = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM document_chunks")
        total_chunks = cursor.fetchone()["count"]

        cursor.execute("SELECT category, COUNT(*) as count FROM documents GROUP BY category")
        categories = {r["category"]: r["count"] for r in cursor.fetchall()}

        cursor.execute("SELECT status, COUNT(*) as count FROM documents GROUP BY status")
        status_summary = {r["status"]: r["count"] for r in cursor.fetchall()}

        return {
            "total_documents": total_docs,
            "total_chunks": total_chunks,
            "categories": categories,
            "status_summary": status_summary
        }
