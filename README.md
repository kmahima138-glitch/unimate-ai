# 🎓 UniMate AI — Intelligent University Assistant

> **Retrieval-Augmented Generation (RAG) System for University Academic & Administrative Knowledge**  
> Grounded question answering, verifiable source citations, smart notice extraction, and AI study quiz assistant.

---

## 🌟 Overview & Highlights

UniMate AI is an end-to-end GenAI application designed to solve the problem of university policy ambiguity and administrative question overload. Unlike generic chatbots that hallucinate rules, UniMate AI:
1. **Indexes official PDFs and DOCX files** into semantic vector embeddings with page-level preservation.
2. **Constrains LLM generation strictly to retrieved evidence** — if a rule is not documented, it acknowledges insufficient information rather than inventing policies.
3. **Provides interactive source citations** with exact page numbers, document titles, and excerpt previews.
4. **Supports Hindi & English** with cross-lingual academic concept matching.
5. **Automatically extracts dates and deadlines** from official notices into an Academic Deadlines calendar.
6. **Features an AI Study Assistant** for generating practice MCQs with explanations and revision flashcards.
7. **Includes an Administrator Dashboard** for document management, chunk inspection, and unanswered query analytics.

---

## 🏗️ Architecture

```
User Query (English / Hindi)
         │
         ▼
[Language & Concept Expander]
         │
         ▼
[Dense Semantic Retrieval (Vector Store)] ──> Top-K Relevant Chunks (with Page Numbers)
         │
         ▼
[Evidence Sufficiency & Conflict Detector]
         │
         ├── If Insufficient ──────> "Information not found in university documents"
         │
         └── If Evidence Found ───> [Grounding Prompt Engine]
                                               │
                                               ▼
                                      [LLM Generation (Gemini)]
                                               │
                                               ▼
                         Grounded Answer + Verifiable Citations (Page #)
```

---

## 🚀 Quick Start (Local Setup)

### Prerequisites
- Python 3.9+ (Python 3.9 through 3.13 supported)

### 1. Launch the Application
Run the automated launch script from the project root:
```bash
cd unimate-ai
./run.sh
```
Or run directly with Python:
```bash
./venv/bin/python run.py
```

### 2. Access the Web Portal
Open your browser at:
- **Web Portal:** `http://localhost:8000`
- **Interactive OpenAPI Docs:** `http://localhost:8000/docs`

---

## ⚙️ Configuration (`.env`)

Copy `.env.example` to `.env`:
```ini
APP_NAME=UniMate AI
PORT=8000
HOST=0.0.0.0

# Optional: Google Gemini API Key
# If omitted, UniMate AI runs in deterministic offline grounded-rule mode.
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

# Storage
DATA_DIR=data
DB_URL=sqlite:///data/unimate.db
UPLOAD_DIR=data/uploads
CHROMA_PERSIST_DIR=data/chromadb

# RAG Parameters
CHUNK_SIZE=600
CHUNK_OVERLAP=100
TOP_K_RETRIEVAL=4
SIMILARITY_THRESHOLD=0.38
```

---

## 🧪 Automated Testing

UniMate AI includes a comprehensive unit and integration test suite covering PDF/DOCX parsing, chunking with overlap, semantic retrieval, citation mapping, Hindi language handling, and strict insufficient-evidence refusal:

```bash
python -m pip install -r requirements.txt
python -m pytest backend/tests/ -v
```

### Continuous Integration

GitHub Actions runs the test suite on pushes to `main` and on pull requests targeting `main`, using Python 3.11. The tests run in offline mode and do not require a Gemini API key. A failed check will appear on the pull request with logs explaining the failure.

### Verified Test Results:
- `test_chunking_preserves_page_numbers_and_metadata`: PASSED
- `test_chunking_overlap`: PASSED
- `test_rag_attendance_query_with_citations`: PASSED
- `test_rag_insufficient_evidence_refusal`: PASSED
- `test_rag_hindi_language_support`: PASSED
- `test_retrieval_attendance_policy`: PASSED
- `test_retrieval_insufficient_evidence`: PASSED
- `test_conflict_detection_logic`: PASSED
- `test_extract_pdf_pages_and_metadata`: PASSED
- `test_extract_docx_paragraphs`: PASSED

---

## 📋 Verified Demo Scenarios

| Scenario | Question / Action | Expected Result |
|---|---|---|
| **Attendance Policy** | *"What is the minimum attendance required to appear in exams?"* | Returns 75% requirement with condonation up to 65% on medical grounds, citing **Academic Regulations 2026, Page 2**. |
| **Insufficient Evidence Refusal** | *"What is the policy for quantum teleportation in dorms?"* | Refuses to hallucinate: *"Based on the official university documents currently indexed, I do not have enough information to answer this question."* |
| **Notice Deadline Extraction** | Upload or view *End-Semester Examination Circular*. | AI extracts the deadline **25th November 2026** and populates the Academic Deadlines calendar. |
| **Hindi Query** | *"परीक्षा में बैठने के लिए न्यूनतम उपस्थिति कितनी होनी चाहिए?"* | Responds in Hindi stating 75% attendance rule with page citations. |
| **Study Quiz Generator** | Click *Generate Practice MCQs* on Study Assistant tab. | Synthesizes 4 multiple-choice practice questions with option explanations and disclaimer. |
| **Admin Inspection** | Navigate to *Admin Portal* -> Click *Inspect Chunks*. | Displays page-by-page chunk boundaries, token IDs, and text vectors. |

---

## 📂 Project Structure

```text
unimate-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application & SPA router
│   │   ├── api/
│   │   │   ├── chat.py                 # RAG chat & conversation history endpoints
│   │   │   ├── documents.py            # Upload, list, status, delete, chunk inspect
│   │   │   ├── notices.py              # Notice board & calendar deadlines
│   │   │   ├── study.py                # Quiz, flashcards, study assistant
│   │   │   └── analytics.py            # Feedback, unanswered questions, metrics
│   │   ├── core/
│   │   │   └── config.py               # Settings & environment variables
│   │   ├── db/
│   │   │   └── database.py             # SQLite database manager & schema init
│   │   ├── schemas/                    # Pydantic validation schemas
│   │   ├── services/
│   │   │   ├── text_extraction.py      # PyMuPDF (fitz) & python-docx extractors
│   │   │   ├── chunking.py             # Recursive token chunker with overlap
│   │   │   ├── embeddings.py           # Dense 384-dim semantic embedding engine
│   │   │   ├── vector_store.py         # Persistent vector storage & hybrid search
│   │   │   ├── retrieval.py            # Cross-lingual expansion & score thresholding
│   │   │   ├── llm_service.py          # Gemini API + grounded offline fallback
│   │   │   ├── rag_pipeline.py         # End-to-end RAG orchestrator
│   │   │   ├── notice_service.py       # Circular parsing & date extraction
│   │   │   └── study_service.py        # Practice MCQ & flashcard generator
│   │   └── prompts/
│   │       └── system_grounding.py     # Grounding guardrails & citation instructions
│   ├── tests/                          # 10 automated pytest suites
│   └── scripts/
│       ├── generate_sample_docs.py     # Creates sample regulations, circulars & docs
│       └── seed_knowledge_base.py      # Indexes initial university knowledge base
├── frontend/
│   └── index.html                      # Full React 18 SPA with Tailwind CSS & Lucide icons
├── data/
│   ├── sample_docs/                    # Sample PDFs and DOCX files
│   └── uploads/                        # Uploaded document storage
├── run.py                              # Server launcher
├── run.sh                              # Single-command executable script
├── requirements.txt
├── .env.example
└── README.md
```

Authored by Mahima Kumari
