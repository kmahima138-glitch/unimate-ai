import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["app"] == "UniMate AI"

def test_api_documents_list():
    res = client.get("/api/documents")
    assert res.status_code == 200
    docs = res.json()
    assert len(docs) >= 3
    titles = [d["title"] for d in docs]
    assert any("Academic Regulations" in t for t in titles)

def test_api_chat_attendance():
    payload = {
        "message": "What is the minimum attendance required?",
        "language": "en"
    }
    res = client.post("/api/chat/message", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "75%" in data["content"] or "attendance" in data["content"].lower()
    assert len(data["citations"]) > 0

def test_api_chat_unknown():
    payload = {
        "message": "What is the university policy on time travel?",
        "language": "en"
    }
    res = client.post("/api/chat/message", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["evidence_level"] == "insufficient"
    assert len(data["citations"]) == 0

def test_api_notices_and_deadlines():
    res_notices = client.get("/api/notices")
    assert res_notices.status_code == 200
    notices = res_notices.json()
    assert len(notices) >= 1

    res_deadlines = client.get("/api/notices/deadlines")
    assert res_deadlines.status_code == 200
    deadlines = res_deadlines.json()
    assert len(deadlines) >= 1
    assert any("25th November 2026" in d["event_date"] for d in deadlines)

def test_api_study_quiz():
    payload = {
        "topic": "Academic Regulations",
        "num_questions": 3
    }
    res = client.post("/api/study/quiz", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["questions"]) >= 1
    assert "disclaimer" in data

def test_api_analytics_overview():
    res = client.get("/api/analytics/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["total_documents"] >= 3
    assert data["total_chunks"] >= 5

def test_api_auth_login():
    res_student = client.post("/api/auth/login", json={"email": "kmahima138@gmail.com", "role": "student"})
    assert res_student.status_code == 200
    s_data = res_student.json()
    assert s_data["user"]["name"] == "Mahima Kumari"
    assert s_data["user"]["course"] == "MCA"
    assert s_data["user"]["semester"] == 3

    res_admin = client.post("/api/auth/login", json={"email": "admin.academic@uni.edu", "role": "admin"})
    assert res_admin.status_code == 200
    a_data = res_admin.json()
    assert a_data["user"]["role"] == "admin"
    assert "Admin" in a_data["user"]["name"]
