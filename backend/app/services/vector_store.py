import os
import json
import sqlite3
import numpy as np
from typing import List, Dict, Any, Optional
from backend.app.core.config import settings

class VectorStore:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DB_URL.replace("sqlite:///", "")

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_vector_table(self):
        with self._get_connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS vector_chunks (
                chunk_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                page_number INTEGER NOT NULL,
                document_title TEXT NOT NULL,
                category TEXT NOT NULL,
                text TEXT NOT NULL,
                embedding_blob BLOB NOT NULL,
                metadata_json TEXT,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
            )
            """)
            conn.commit()

    def add_chunks(self, document_id: str, document_title: str, category: str, chunks: List[Any], embeddings: List[List[float]]):
        """
        Stores chunks and their embedding vectors in the persistent vector table.
        Removes existing chunks for the same document to prevent duplicates.
        """
        self.delete_by_document_id(document_id)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for chunk, emb in zip(chunks, embeddings):
                emb_array = np.array(emb, dtype=np.float32)
                cursor.execute("""
                INSERT INTO vector_chunks (
                    chunk_id, document_id, chunk_index, page_number,
                    document_title, category, text, embedding_blob, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chunk.chunk_id,
                    document_id,
                    chunk.chunk_index,
                    chunk.page_number,
                    document_title,
                    category,
                    chunk.text,
                    emb_array.tobytes(),
                    json.dumps(chunk.metadata)
                ))
            conn.commit()

    def delete_by_document_id(self, document_id: str):
        """Removes all chunks associated with a document."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM vector_chunks WHERE document_id = ?", (document_id,))
            conn.commit()

    def search(self, query_embedding: List[float], query_text: str = "", top_k: int = 4, min_score: float = 0.20, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Performs semantic similarity search with hybrid keyword boosting.
        Returns ranked list of chunks with similarity scores and page metadata.
        """
        q_vec = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 1e-6:
            q_vec = q_vec / q_norm

        with self._get_connection() as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute("SELECT * FROM vector_chunks WHERE category = ?", (category,))
            else:
                cursor.execute("SELECT * FROM vector_chunks")
            
            rows = cursor.fetchall()

        if not rows:
            return []

        scored_chunks = []
        q_words = set(query_text.lower().split()) if query_text else set()

        for row in rows:
            emb_blob = row["embedding_blob"]
            c_vec = np.frombuffer(emb_blob, dtype=np.float32)
            c_norm = np.linalg.norm(c_vec)
            if c_norm > 1e-6:
                c_vec = c_vec / c_norm

            # Cosine similarity
            cosine_sim = float(np.dot(q_vec, c_vec))

            # Hybrid keyword overlap boost
            keyword_boost = 0.0
            if q_words:
                text_lower = row["text"].lower()
                matches = sum(1 for w in q_words if len(w) > 3 and w in text_lower)
                keyword_boost = min(0.20, matches * 0.05)

            final_score = cosine_sim + keyword_boost

            if final_score >= min_score:
                scored_chunks.append({
                    "chunk_id": row["chunk_id"],
                    "document_id": row["document_id"],
                    "chunk_index": row["chunk_index"],
                    "page_number": row["page_number"],
                    "document_title": row["document_title"],
                    "category": row["category"],
                    "text": row["text"],
                    "metadata": json.loads(row["metadata_json"] or "{}"),
                    "similarity_score": round(final_score, 4),
                    "raw_cosine": round(cosine_sim, 4)
                })

        # Rank by final score descending
        scored_chunks.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_chunks[:top_k]

    def count_chunks(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM vector_chunks")
            return cursor.fetchone()["count"]

vector_store = VectorStore()
vector_store.init_vector_table()
