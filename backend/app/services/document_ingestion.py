import os
import uuid
import shutil
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import UploadFile

from backend.app.core.config import settings
from backend.app.db.database import db
from backend.app.services.text_extraction import TextExtractionService
from backend.app.services.chunking import ChunkingService
from backend.app.services.embeddings import embedding_service
from backend.app.services.vector_store import vector_store

class DocumentIngestionService:
    def __init__(self):
        self.extractor = TextExtractionService()
        self.chunker = ChunkingService()
        self.embedder = embedding_service
        self.vector_store = vector_store

    def create_pending_document(
        self,
        filename: str,
        title: str,
        category: str,
        file_type: str,
        file_size: int,
        uploaded_by: str = "admin"
    ) -> str:
        doc_id = f"doc_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow().isoformat()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO documents (
                id, title, filename, category, file_path, file_type, 
                file_size, page_count, status, chunk_count, uploaded_by, uploaded_at, version
            ) VALUES (?, ?, ?, ?, '', ?, ?, 0, 'pending', 0, ?, ?, 1)
            """, (doc_id, title, filename, category, file_type, file_size, uploaded_by, now))
            conn.commit()
            
        return doc_id

    def process_document(self, doc_id: str, file_path: str, category: str = "general") -> Dict[str, Any]:
        """
        Executes the ingestion pipeline:
        1. Mark as 'processing'
        2. Extract text & page metadata
        3. Chunk text preserving page references
        4. Generate embeddings
        5. Store in vector database
        6. Mark as 'completed'
        """
        try:
            with db.get_connection() as conn:
                conn.execute("UPDATE documents SET status = 'processing', file_path = ? WHERE id = ?", (file_path, doc_id))
                conn.commit()

            file_ext = os.path.splitext(file_path)[1].lower()
            pages, metadata = self.extractor.extract(file_path, file_ext)

            # Retrieve doc title
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT title FROM documents WHERE id = ?", (doc_id,))
                row = cursor.fetchone()
                doc_title = row["title"] if row else metadata.get("title", "Document")

            # Chunk document
            chunks = self.chunker.chunk_document(
                document_id=doc_id,
                pages=pages,
                doc_metadata={"document_title": doc_title, "category": category}
            )

            if not chunks:
                raise ValueError("No extractable text found in document. May be image-only or scanned PDF.")

            # Generate embeddings
            chunk_texts = [c.text for c in chunks]
            embeddings = self.embedder.embed_batch(chunk_texts)

            # Store in Vector Store
            self.vector_store.add_chunks(
                document_id=doc_id,
                document_title=doc_title,
                category=category,
                chunks=chunks,
                embeddings=embeddings
            )

            # Store chunk records in relational DB for inspectability
            with db.get_connection() as conn:
                cursor = conn.cursor()
                for c in chunks:
                    cursor.execute("""
                    INSERT OR REPLACE INTO document_chunks (id, document_id, chunk_index, text, page_number, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (c.chunk_id, doc_id, c.chunk_index, c.text, c.page_number, "{}"))

                cursor.execute("""
                UPDATE documents 
                SET status = 'completed', page_count = ?, chunk_count = ?, error_message = NULL
                WHERE id = ?
                """, (metadata.get("page_count", len(pages)), len(chunks), doc_id))
                conn.commit()

            return {
                "id": doc_id,
                "status": "completed",
                "page_count": metadata.get("page_count", len(pages)),
                "chunk_count": len(chunks)
            }

        except Exception as e:
            with db.get_connection() as conn:
                conn.execute(
                    "UPDATE documents SET status = 'failed', error_message = ? WHERE id = ?",
                    (str(e), doc_id)
                )
                conn.commit()
            raise e

    def delete_document(self, doc_id: str) -> bool:
        """Deletes a document, cleans up its chunks from vector store, and deletes physical file."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM documents WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            if not row:
                return False

            file_path = row["file_path"]
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass

            self.vector_store.delete_by_document_id(doc_id)
            cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            conn.commit()
            return True

document_ingestion_service = DocumentIngestionService()
