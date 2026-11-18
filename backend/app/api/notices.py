from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from backend.app.schemas.notice import NoticeCreate, NoticeResponse, AcademicEventResponse
from backend.app.services.notice_service import notice_service
from backend.app.db.database import db

router = APIRouter(prefix="/api/notices", tags=["Notices"])

@router.get("", response_model=List[NoticeResponse])
def get_notices(
    category: Optional[str] = Query("all"),
    search: Optional[str] = Query(None)
):
    """Retrieves official university notices, optionally filtered by category or search keyword."""
    return notice_service.list_notices(category=category, search=search)

@router.post("", response_model=NoticeResponse)
def create_notice(req: NoticeCreate):
    """Publishes a new university notice and auto-extracts key dates/deadlines."""
    return notice_service.extract_and_publish_notice(
        title=req.title,
        content=req.summary,
        document_id=req.document_id,
        category=req.category
    )

@router.get("/deadlines", response_model=List[AcademicEventResponse])
def get_upcoming_deadlines():
    """Returns calendar of upcoming academic deadlines, examinations, and events."""
    return notice_service.list_academic_events()
