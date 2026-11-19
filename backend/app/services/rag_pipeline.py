import uuid
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.app.services.retrieval import retrieval_service
from backend.app.services.llm_service import llm_service
from backend.app.db.database import db

class RAGPipeline:
    def __init__(self):
        self.retrieval = retrieval_service
        self.llm = llm_service

    def get_conversation_history(self, conversation_id: str, limit: int = 6) -> List[Dict[str, str]]:
        if not conversation_id:
            return []
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT role, content FROM messages 
            WHERE conversation_id = ? 
            ORDER BY created_at DESC LIMIT ?
            """, (conversation_id, limit))
            rows = cursor.fetchall()
            # Return in chronological order
            return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

    def is_conversational_or_greeting(self, query: str) -> bool:
        """Detects whether a query is a greeting, identity, or capability question about the bot itself."""
        import re
        q = query.strip().lower()
        q_clean = re.sub(r"[^\w\s]", "", q).strip()
        tokens = q_clean.split()

        greetings = {"hi", "hello", "hey", "hola", "namaste", "good morning", "good evening", "good afternoon"}
        if q_clean in greetings or (len(tokens) <= 2 and any(t in greetings for t in tokens)):
            return True

        capability_patterns = [
            r"(?:what|how)\s+(?:can|do)\s+you\s+do",
            r"(?:who|what)\s+are\s+you",
            r"(?:tell|explain)\s+(?:me\s+)?about\s+(?:yourself|you)",
            r"(?:what\s+is\s+your\s+purpose|what\s+are\s+your\s+features)",
            r"(?:what\s+services|what\s+can\s+i\s+ask|how\s+can\s+you\s+help)",
            r"help\s+me",
            r"^(?:help|\?)$",
            r"(?:aap\s+kya\s+kar\s+sakte\s+ho|tum\s+kya\s+karte\s+ho|aap\s+kaun\s+ho|kya\s+karte\s+ho)"
        ]
        for pat in capability_patterns:
            if re.search(pat, q_clean):
                return True
        return False

    def run(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = "usr_student_demo",
        language: str = "auto"
    ) -> Dict[str, Any]:
        """
        Executes the end-to-end RAG pipeline:
        1. Ensure conversation exists.
        2. Store user message in DB.
        3. Check for greeting/capability inquiries.
        4. Retrieve chunks with score thresholding & conflict detection.
        5. Synthesize grounded answer with strict evidence boundaries.
        6. Build verifiable source citations.
        7. Store assistant message with citations & evidence rating.
        """
        now = datetime.utcnow().isoformat()

        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Create conversation if not provided
            if not conversation_id:
                conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
                conv_title = query[:40] + ("..." if len(query) > 40 else "")
                cursor.execute("""
                INSERT INTO conversations (id, user_id, title, language, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (conversation_id, user_id, conv_title, language, now, now))
            else:
                cursor.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conversation_id))

            # Record user message
            user_msg_id = f"msg_{uuid.uuid4().hex[:12]}"
            cursor.execute("""
            INSERT INTO messages (id, conversation_id, role, content, evidence_level, citations_json, created_at)
            VALUES (?, ?, 'user', ?, 'strong', '[]', ?)
            """, (user_msg_id, conversation_id, query, now))
            conn.commit()

        # Handle Conversational Greetings & Bot Capability Inquiries
        if self.is_conversational_or_greeting(query):
            user_name = "Mahima"
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM users WHERE id = ?", (user_id,))
                user_row = cursor.fetchone()
                if user_row and user_row["name"]:
                    user_name = user_row["name"]

            lang = self.llm.detect_language(query)
            intro_answer = self.llm.get_assistant_introduction(user_name=user_name, lang=lang)

            asst_msg_id = f"msg_{uuid.uuid4().hex[:12]}"
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO messages (id, conversation_id, role, content, evidence_level, citations_json, created_at)
                VALUES (?, ?, 'assistant', ?, 'strong', '[]', ?)
                """, (asst_msg_id, conversation_id, intro_answer, now))
                conn.commit()

            return {
                "id": asst_msg_id,
                "conversation_id": conversation_id,
                "role": "assistant",
                "content": intro_answer,
                "evidence_level": "strong",
                "citations": [],
                "created_at": now
            }

        # Retrieve relevant chunks from vector store
        chunks, evidence_level, has_conflict = self.retrieval.retrieve(query)

        # Get recent conversation history for multi-turn context
        history = self.get_conversation_history(conversation_id)

        # Generate answer with LLM
        answer = self.llm.generate_grounded_answer(
            query=query,
            retrieved_chunks=chunks,
            conversation_history=history,
            evidence_level=evidence_level,
            has_conflict=has_conflict
        )

        # Build citations mapping strictly to retrieved chunks
        citations = []
        if evidence_level != "insufficient" and chunks:
            seen_pages = set()
            for chunk in chunks:
                page_key = (chunk["document_id"], chunk["page_number"])
                if page_key in seen_pages:
                    continue
                seen_pages.add(page_key)

                citations.append({
                    "document_id": chunk["document_id"],
                    "document_title": chunk["document_title"],
                    "page_number": chunk["page_number"],
                    "snippet": chunk["text"][:220] + ("..." if len(chunk["text"]) > 220 else ""),
                    "similarity_score": chunk["similarity_score"]
                })

        # Record assistant response
        asst_msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO messages (id, conversation_id, role, content, evidence_level, citations_json, created_at)
            VALUES (?, ?, 'assistant', ?, ?, ?, ?)
            """, (asst_msg_id, conversation_id, answer, evidence_level, json.dumps(citations), now))
            conn.commit()

        return {
            "id": asst_msg_id,
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": answer,
            "evidence_level": evidence_level,
            "citations": citations,
            "created_at": now
        }

rag_pipeline = RAGPipeline()
