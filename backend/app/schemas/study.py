from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class MCQQuestion(BaseModel):
    id: int
    question: str
    options: List[str]
    correct_option_index: int
    explanation: str
    source_reference: Optional[str] = None

class QuizGenerateRequest(BaseModel):
    document_id: Optional[str] = None
    topic: Optional[str] = None
    num_questions: Optional[int] = 5
    difficulty: Optional[str] = "intermediate"

class QuizResponse(BaseModel):
    topic: str
    document_title: Optional[str] = None
    questions: List[MCQQuestion]
    disclaimer: str = "These questions are generated for self-practice from university materials and do not constitute official exam question papers."

class Flashcard(BaseModel):
    id: int
    front: str
    back: str
    category: Optional[str] = None

class FlashcardGenerateRequest(BaseModel):
    document_id: Optional[str] = None
    topic: Optional[str] = "Key Concepts"

class FlashcardResponse(BaseModel):
    topic: str
    document_title: Optional[str] = None
    flashcards: List[Flashcard]

class SyllabusSummaryResponse(BaseModel):
    document_id: str
    document_title: str
    overview: str
    key_modules: List[Dict[str, Any]]
    recommended_books: List[str]
    grading_scheme: Optional[str] = None
