import pytest
from backend.app.services.retrieval import retrieval_service

def test_retrieval_attendance_policy():
    chunks, evidence_level, has_conflict = retrieval_service.retrieve("What is the minimum attendance required?")
    assert len(chunks) > 0
    assert evidence_level in ["strong", "partial"]
    top_text = chunks[0]["text"]
    assert "75%" in top_text or "attendance" in top_text.lower()
    assert chunks[0]["page_number"] == 2

def test_retrieval_insufficient_evidence():
    # Ask about rocket propulsion or irrelevant trivia
    chunks, evidence_level, _ = retrieval_service.retrieve("What is the warp speed of the starship Enterprise?")
    assert evidence_level == "insufficient" or len(chunks) == 0

def test_conflict_detection_logic():
    chunks_with_conflict = [
        {"document_id": "doc_1", "text": "Minimum attendance required is 75% for regular courses.", "page_number": 2},
        {"document_id": "doc_2", "text": "Minimum attendance required is 85% for scholarship students.", "page_number": 1}
    ]
    assert retrieval_service._detect_conflicts(chunks_with_conflict) is True
