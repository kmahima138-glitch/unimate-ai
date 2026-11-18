from typing import Optional, List
from pydantic import BaseModel

class NoticeCreate(BaseModel):
    title: str
    category: Optional[str] = "general"
    summary: str
    affected_dept: Optional[str] = "All Departments"
    affected_semester: Optional[str] = "All Semesters"
    action_required: Optional[str] = None
    deadline: Optional[str] = None
    document_id: Optional[str] = None

class NoticeResponse(BaseModel):
    id: str
    document_id: Optional[str] = None
    title: str
    category: str
    summary: str
    affected_dept: Optional[str] = None
    affected_semester: Optional[str] = None
    action_required: Optional[str] = None
    deadline: Optional[str] = None
    published_at: str

class AcademicEventResponse(BaseModel):
    id: str
    title: str
    event_date: str
    event_type: str # 'exam', 'registration', 'deadline', 'holiday', 'event'
    audience: Optional[str] = "All Students"
    source_document_id: Optional[str] = None
    source_page: Optional[int] = None
