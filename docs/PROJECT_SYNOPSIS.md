# PROJECT SYNOPSIS

# UniMate AI: An Intelligent University Knowledge Assistant Powered by Grounded Retrieval-Augmented Generation (RAG)

**Candidate Name:** Mahima Kumari  
**University Seat Number (USN):** MCA25SCA113  
**Semester & Program:** 3rd Semester, Master of Computer Applications (MCA)  
**Specialization:** Artificial Intelligence & Machine Learning (AI/ML)  
**Department:** Department of Computer Applications  
**Institution:** Dayananda Sagar University (DSU), Bengaluru, Karnataka, India  
**Academic Year:** 2026–2027  

---

## 1. INTRODUCTION

In contemporary universities, thousands of enrolled students interact daily with a vast array of institutional rules, circulars, examination ordinances, syllabus revisions, and administrative deadlines. Typically, this vital information is published across static notice boards, disorganized intranet portals, or lengthy PDF handbook archives. Consequently, students struggle to locate specific regulatory clauses (such as attendance condonation thresholds, examination fee deadlines, or revaluation procedures), resulting in administrative congestion, repetitive manual queries at registrar desks, and accidental student non-compliance.

Recent advances in Generative Artificial Intelligence (GenAI) and Large Language Models (LLMs) offer intuitive conversational interfaces; however, out-of-the-box LLMs suffer from three critical flaws in institutional environments:
1. **Hallucination:** Models fabricate non-existent university policies when uncertain.
2. **Lack of Verifiable Source Citations:** Answers cannot be cross-referenced with official page numbers.
3. **Information Staleness:** LLMs cannot track newly published circulars without expensive retraining.

This project, **UniMate AI**, introduces a production-ready, domain-grounded conversational university assistant powered by **Retrieval-Augmented Generation (RAG)**. UniMate AI bridges the gap between student inquiries and official documentation by coupling dense vector retrieval over indexed university documents with constrained, citation-backed LLM response generation.

---

## 2. PROBLEM STATEMENT

*"To design and develop a trustworthy, multilingual, and grounded AI assistant for university students and administrators that ingests official PDF/DOCX documents, executes semantic retrieval over overlapping vectorized chunks, strictly constraints answer synthesis to retrieved institutional evidence with verifiable page-level citations, and autonomously refuses to fabricate answers when official evidence is absent."*

---

## 3. OBJECTIVES OF THE PROJECT

1. **Explicit Document Intelligence Pipeline:** Build an automated ingestion pipeline using PyMuPDF and python-docx that extracts text page-by-page while preserving structural document metadata.
2. **Context-Aware Semantic Chunking & Vectorization:** Partition extracted text into overlapping chunks (~600 characters with 100-character overlap) to preserve contextual continuity, vectorizing chunks into dense 384-dimensional embeddings.
3. **Grounded RAG & Anti-Hallucination Guardrails:** Implement a semantic retrieval engine with cosine similarity and hybrid keyword boosting. Enforce strict evidence thresholding that refuses ungrounded inquiries instead of hallucinating.
4. **Verifiable Page-Level Source Citations:** Map every factual assertion back to the source document name, exact page number, and original excerpt preview.
5. **Smart Notice & Deadline Extraction:** Parse administrative circulars and automatically extract submission deadlines, affected departments, and action items into a searchable academic calendar.
6. **AI Study Assistant:** Automatically generate self-study practice Multiple Choice Questions (MCQs) with pedagogical answer explanations and flashcards from uploaded course syllabi.
7. **Administrative Transparency & Governance:** Deliver an administrative portal with live document indexing states, vector chunk inspectability, and unanswered query gap analysis.
8. **Cloud Containerization & Production Deployment:** Package the full-stack system using Docker and deploy to public cloud infrastructure with zero external database dependencies.

---

## 4. COMPARISON: EXISTING SYSTEM VS. PROPOSED SYSTEM

| Parameter | Existing Institutional Systems | Generic LLM Chatbots | Proposed UniMate AI |
|---|---|---|---|
| **Information Discovery** | Manual keyword searching across multiple PDFs | Conversational natural language | Conversational natural language |
| **Grounding & Accuracy** | High (static documents), but hard to navigate | Low (prone to institutional hallucinations) | **Strictly Grounded** in institutional documents |
| **Source Citations** | Manual manual inspection | Non-existent or hallucinated links | **Exact Document Title & Page Number** |
| **Missing Info Behavior** | Silence / 404 Not Found | Confident fabrication of false rules | **Honest Insufficient-Evidence Refusal** |
| **Notice Deadlines** | Static text notices | Requires explicit manual prompt pasting | **Automated Extraction to Calendar** |
| **Multilingual Support** | Typically English only | Varies, often ungrounded in regional context | **Cross-lingual English & Hindi Support** |
| **Study Revision Tools** | Not integrated | Generic non-syllabus practice questions | **Grounded Syllabus MCQs & Flashcards** |
| **Admin Oversight** | None | Closed black-box | **Chunk Inspector & Unanswered Logs** |

---

## 5. PROPOSED SYSTEM ARCHITECTURE

```
+───────────────────────────────────────────────────────────────────────────+
|                          CLIENT PRESENTATION TIER                         |
|  React 18 SPA • Tailwind CSS • Lucide UI • Markdown & KaTeX Typography    |
|  [Student Chat Portal]   [Deadlines Tracker]   [AI Study]   [Admin Portal]|
+─────────────────────────────────────┬─────────────────────────────────────+
                                      │ REST / JSON (FastAPI)
                                      ▼
+───────────────────────────────────────────────────────────────────────────+
|                           APPLICATION & RAG TIER                          |
|  FastAPI Gateway • Pydantic Schemas • CORS • Session Token Auth           |
|                                                                           |
|  ┌───────────────────────┐  ┌───────────────────────┐  ┌────────────────┐ |
|  | Document Ingestion    |  | Semantic Retrieval    |  | LLM Grounding  | |
|  | • PyMuPDF (PDF)       |  | • 384-dim Embeddings  |  | • Gemini /     | |
|  | • python-docx (DOCX)  |  | • Hybrid Keyword Boost|  |   Deterministic| |
|  | • 600-char Chunking   |  | • Cosine Similarity   |  |   Synthesizer  | |
|  | • Page Preservation   |  | • Threshold Gating    |  | • Citations Gen| |
|  └───────────────────────┘  └───────────────────────┘  └────────────────┘ |
+─────────────────────────────────────┬─────────────────────────────────────+
                                      │
                                      ▼
+───────────────────────────────────────────────────────────────────────────+
|                            PERSISTENT DATA TIER                           |
|  [SQLite Database: unimate.db]      [Vector Store: vector_chunks BLOBs]   |
|  • Users & Profiles (Mahima Kumari) • 384-dim Dense Vector Index          |
|  • Conversations & Chat History     • Page Number & Chunk Sequence        |
|  • Notices & Calendar Events        [Raw Document Storage: data/uploads/] |
+───────────────────────────────────────────────────────────────────────────+
```

---

## 6. FUNCTIONAL MODULES BREAKDOWN

1. **Document Intelligence & Ingestion Module:**
   Validates uploaded files (max 25MB), extracts text page-by-page preserving 1-indexed page boundaries, applies recursive splitting with sentence and punctuation awareness, computes 384-dimensional dense semantic vectors, and records indexing state (`pending` $\rightarrow$ `processing` $\rightarrow$ `completed` / `failed`).
2. **Dense Semantic Retrieval & Evidence Evaluation Module:**
   Performs cosine similarity search against stored chunk vectors with hybrid keyword boosting for numerical regulatory clauses (e.g., "75%", "Nov 25", "Rs. 500"). Evaluates top-chunk similarity scores:
   * $\text{Score} \ge 0.52$: Strong Evidence.
   * $0.38 \le \text{Score} < 0.52$: Partial Evidence.
   * $\text{Score} < 0.38$: Insufficient Evidence $\rightarrow$ Triggers honest refusal.
3. **Conversational RAG Assistant Module:**
   Synthesizes factual answers strictly from retrieved evidence. Formats verifiable source citation badges with clickable page numbers and text excerpts. Handles conversational greetings (introducing capabilities to students by name) and provides cross-lingual English and Hindi query processing.
4. **Smart Notice & Circular Intelligence Module:**
   Parses official circulars, regex-extracts key submission deadlines, affected departments, and action requirements, and automatically populates the Academic Deadlines calendar.
5. **AI Study Assistant Module:**
   Analyzes uploaded syllabus documents to synthesize 4-option practice Multiple Choice Questions (MCQs) with comprehensive pedagogical explanations and revision flashcards.
6. **Administrative Dashboard & Analytics Module:**
   Provides document lifecycle management (upload, delete, re-index), knowledge-base chunk inspection, and logs unanswered/low-evidence student queries to identify gaps in official documentation.
7. **Authentication & Role-Based Access Control:**
   Maintains distinct Student (Mahima Kumari, MCA 3rd Sem) and Administrator (Dr. Priya Mehta, Academic Registrar) access profiles with protected administrative route guards.

---

## 7. TECHNICAL SPECIFICATIONS & STACK

* **Frontend:** React 18, Tailwind CSS, Lucide Icons, Modern Single Page Architecture.
* **Backend:** Python 3.11 / 3.9, FastAPI, Uvicorn ASGI Server, Pydantic v2.
* **Database & Vector Store:** SQLite (Relational metadata, conversations, and dense 384-dimensional embedding BLOBs with vector cosine search).
* **Document Parsers:** PyMuPDF (`fitz` 1.26+) for PDFs, `python-docx` for Word documents.
* **LLM Engine:** Google Gemini API (`gemini-2.5-flash`) with resilient, zero-latency deterministic offline grounded fallback.
* **Containerization & Deployment:** Docker, Git, Render Cloud Platform (Live at `https://unimate-ai-io01.onrender.com`).

---

## 8. HARDWARE & SOFTWARE REQUIREMENTS

### Software Requirements
* **Operating System:** macOS Sonoma / Linux Ubuntu 22.04 LTS / Windows 11
* **Runtime Environment:** Python 3.9.6 or higher
* **Package Management:** pip 24.0+
* **Container Engine:** Docker Engine 24.0+ / Docker Compose v2
* **Web Browser:** Google Chrome, Mozilla Firefox, or Safari (modern evergreen browsers)

### Hardware Requirements
* **Processor:** Intel Core i5 / AMD Ryzen 5 or Apple Silicon (M1/M2/M3/M4)
* **RAM:** 4 GB minimum (8 GB recommended)
* **Storage:** 2 GB available disk space for local environment and document storage
* **Network:** Standard broadband connection for cloud deployment and live LLM APIs

---

## 9. FEASIBILITY STUDY

* **Technical Feasibility:** Python and FastAPI offer industry-standard async throughput and modular design. PyMuPDF provides sub-second PDF text extraction. Storing 384-dimensional dense vectors in SQLite ensures zero external infrastructure dependency and high reliability.
* **Operational Feasibility:** The clean, responsive web interface requires no prior technical training for university students. The Admin portal allows non-technical registrar staff to upload circulars with one click.
* **Economic Feasibility:** The architecture utilizes open-source components and lightweight embeddings that operate without expensive GPU clusters, making it viable for deployment on free or low-cost cloud tiers (Render, Hugging Face).

---

## 10. EXPECTED OUTCOMES & DELIVERABLES

1. **Fully Functional Deployed Web Application:** Publicly accessible, responsive portal featuring Student Chat, Dashboard, Notices, Study Assistant, and Admin Portals.
2. **Grounded Question Answering Engine:** Zero-hallucination institutional conversational agent with verifiable page-level citations.
3. **Automated Academic Deadlines Calendar:** Real-time visibility into examination dates and registration deadlines.
4. **Complete Source Code Repository:** Open-source, production-grade GitHub repository with 19 automated unit and integration tests passing at 100%.
5. **Comprehensive Project Documentation:** IEEE-compliant Project Abstract, Project Synopsis, and Major Technical Project Report.

---

## 11. IEEE REFERENCES

1. P. Lewis, E. Perez, A. Piktus, et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 33, pp. 9459–9474, 2020.
2. J. Devlin, M. W. Chang, K. Lee, and K. Toutanova, "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding," in *Proc. NAACL-HLT*, pp. 4171–4186, 2019.
3. N. Reimers and I. Gurevych, "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks," in *Proc. 2019 Conf. EMNLP*, pp. 3982–3992, 2019.
4. S. Robertson and H. Zaragoza, "The Probabilistic Relevance Framework: BM25 and Beyond," *Foundations and Trends in Information Retrieval*, vol. 3, no. 4, pp. 333–389, 2009.
5. S. Bubeck, V. Chandrasekaran, R. Eldan, et al., "Sparks of Artificial General Intelligence: Early experiments with GPT-4," *arXiv preprint arXiv:2303.12712*, 2023.
