import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from backend.app.schemas.chat import (
    ChatMessageRequest,
    MessageResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationDetailResponse,
    Citation
)
from backend.app.services.rag_pipeline import rag_pipeline
from backend.app.db.database import db

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("/message", response_model=MessageResponse)
def post_chat_message(req: ChatMessageRequest):
    """
    Core RAG question answering endpoint:
    Retrieves evidence, verifies sufficiency, and generates grounded answer with citations.
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    result = rag_pipeline.run(
        query=req.message,
        conversation_id=req.conversation_id,
        user_id=req.user_id,
        language=req.language or "auto"
    )
    return result

@router.get("/conversations", response_model=List[ConversationResponse])
def list_conversations(user_id: Optional[str] = "usr_student_demo"):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT c.*, COUNT(m.id) as message_count 
        FROM conversations c
        LEFT JOIN messages m ON c.id = m.conversation_id
        WHERE c.user_id = ?
        GROUP BY c.id
        ORDER BY c.updated_at DESC
        """, (user_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

@router.post("/conversations", response_model=ConversationResponse)
def create_conversation(req: ConversationCreate):
    import uuid
    from datetime import datetime
    conv_id = f"conv_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO conversations (id, user_id, title, language, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (conv_id, req.user_id, req.title or "New Conversation", req.language or "en", now, now))
        conn.commit()
    return {
        "id": conv_id,
        "user_id": req.user_id,
        "title": req.title or "New Conversation",
        "language": req.language or "en",
        "created_at": now,
        "updated_at": now,
        "message_count": 0
    }

@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation_details(conversation_id: str):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,))
        conv_row = cursor.fetchone()
        if not conv_row:
            raise HTTPException(status_code=404, detail="Conversation not found.")

        cursor.execute("""
        SELECT * FROM messages 
        WHERE conversation_id = ? 
        ORDER BY created_at ASC
        """, (conversation_id,))
        msg_rows = cursor.fetchall()

        messages = []
        for m in msg_rows:
            citations_raw = m["citations_json"]
            cits = []
            if citations_raw:
                try:
                    cits = json.loads(citations_raw)
                except Exception:
                    cits = []
            messages.append({
                "id": m["id"],
                "conversation_id": m["conversation_id"],
                "role": m["role"],
                "content": m["content"],
                "evidence_level": m["evidence_level"] or "strong",
                "citations": cits,
                "created_at": m["created_at"]
            })

        return {
            "conversation": dict(conv_row),
            "messages": messages
        }

@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: str):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        conn.commit()
    return {"message": "Conversation deleted successfully."}
