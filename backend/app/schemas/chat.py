from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class Citation(BaseModel):
    document_id: str
    document_title: str
    page_number: int
    snippet: str
    similarity_score: Optional[float] = None

class ChatMessageRequest(BaseModel):
    conversation_id: Optional[str] = None
    user_id: Optional[str] = "usr_student_demo"
    message: str
    language: Optional[str] = "auto" # 'auto', 'en', 'hi'

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    evidence_level: str # 'strong', 'partial', 'insufficient'
    citations: List[Citation]
    created_at: str

class ConversationCreate(BaseModel):
    user_id: Optional[str] = "usr_student_demo"
    title: Optional[str] = "New Conversation"
    language: Optional[str] = "en"

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    language: str
    created_at: str
    updated_at: str
    message_count: Optional[int] = 0

class ConversationDetailResponse(BaseModel):
    conversation: ConversationResponse
    messages: List[MessageResponse]
