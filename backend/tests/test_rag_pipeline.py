import pytest
from backend.app.services.rag_pipeline import rag_pipeline

def test_rag_attendance_query_with_citations():
    query = "What is the minimum attendance required to appear in exams?"
    res = rag_pipeline.run(query=query)
    
    assert res["role"] == "assistant"
    assert "75%" in res["content"] or "attendance" in res["content"].lower()
    assert len(res["citations"]) > 0
    top_citation = res["citations"][0]
    assert "Academic Regulations" in top_citation["document_title"]
    assert top_citation["page_number"] == 2

def test_rag_insufficient_evidence_refusal():
    query = "What is the university policy on quantum teleportation equipment in dorms?"
    res = rag_pipeline.run(query=query)
    
    assert res["evidence_level"] == "insufficient"
    assert "do not have enough information" in res["content"].lower() or "not mentioned" in res["content"].lower()
    assert len(res["citations"]) == 0

def test_rag_hindi_language_support():
    query = "परीक्षा में बैठने के लिए न्यूनतम उपस्थिति कितनी होनी चाहिए?"
    res = rag_pipeline.run(query=query)
    
    # Should include Hindi response and 75% or उपस्थिति
    assert "उपस्थिति" in res["content"] or "75%" in res["content"]
    assert len(res["citations"]) > 0

def test_rag_greeting_and_capability_response():
    query = "Hi what can you do"
    res = rag_pipeline.run(query=query)
    
    assert res["role"] == "assistant"
    assert res["evidence_level"] == "strong"
    # Should introduce itself and list core capabilities
    assert "UniMate AI" in res["content"]
    assert "Academic" in res["content"] or "Policies" in res["content"]
    assert "Notices" in res["content"] or "Deadlines" in res["content"]
    # Must NOT return the missing evidence message
    assert "do not have enough information" not in res["content"].lower()
