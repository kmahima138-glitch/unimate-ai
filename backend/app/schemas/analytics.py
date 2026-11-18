from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class FeedbackCreate(BaseModel):
    message_id: str
    user_id: Optional[str] = "usr_student_demo"
    rating: int # 1 for thumbs up, -1 for thumbs down
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: str
    message_id: str
    rating: int
    comment: Optional[str]
    created_at: str

class AnalyticsOverviewResponse(BaseModel):
    total_conversations: int
    total_queries: int
    total_documents: int
    total_chunks: int
    satisfaction_rate: float
    evidence_breakdown: Dict[str, int]
    top_queried_topics: List[Dict[str, Any]]
    unanswered_queries: List[Dict[str, Any]]
