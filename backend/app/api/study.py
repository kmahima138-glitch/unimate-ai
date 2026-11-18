from typing import Optional
from fastapi import APIRouter, HTTPException
from backend.app.schemas.study import (
    QuizGenerateRequest,
    QuizResponse,
    FlashcardGenerateRequest,
    FlashcardResponse,
    SyllabusSummaryResponse
)
from backend.app.services.study_service import study_service

router = APIRouter(prefix="/api/study", tags=["Study Assistant"])

@router.post("/quiz", response_model=QuizResponse)
def generate_practice_quiz(req: QuizGenerateRequest):
    """
    Generates practice MCQs from uploaded course material or syllabus with detailed explanations.
    """
    return study_service.generate_quiz(
        topic=req.topic or "University Course Material",
        document_id=req.document_id,
        num_questions=req.num_questions or 5
    )

@router.post("/flashcards", response_model=FlashcardResponse)
def generate_study_flashcards(req: FlashcardGenerateRequest):
    """
    Generates study flashcards for quick revision.
    """
    return study_service.generate_flashcards(
        topic=req.topic or "Core Concepts",
        document_id=req.document_id
    )
