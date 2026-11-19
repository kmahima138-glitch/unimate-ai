# PROJECT ABSTRACT

## UniMate AI: An Intelligent University Knowledge Assistant Powered by Grounded Retrieval-Augmented Generation (RAG)

**Author:** Mahima Kumari  
**USN:** MCA25SCA113  
**Semester & Program:** 3rd Semester, Master of Computer Applications (MCA – Artificial Intelligence & Machine Learning)  
**Institution:** Department of Computer Applications, School of Engineering, Dayananda Sagar University (DSU), Bengaluru, Karnataka, India  

---

### Abstract

Modern higher education institutions administer complex and continuously evolving academic policies, examination ordinances, fee schedules, circulars, and course syllabi across thousands of students. Traditional dissemination mechanisms—such as static bulletin boards, disparate PDF portals, and administrative front desks—frequently lead to administrative bottlenecks, delayed student actions, and widespread policy ambiguity. While general-purpose Large Language Models (LLMs) provide natural conversational interfaces, their application in institutional governance is critically hindered by domain hallucination, lack of verifiable source attribution, and temporal latency.

To address these limitations, this project presents **UniMate AI**, an institutional conversational knowledge assistant designed on the principles of **Grounded Retrieval-Augmented Generation (RAG)**. The proposed system features an automated, metadata-preserving document ingestion engine capable of extracting structured text from official university documents (PDF and DOCX formats) using PyMuPDF and python-docx. Documents are partitioned via a recursive sliding-window chunking algorithm (600 characters with 100-character overlap) preserving physical page boundaries. Dense 384-dimensional semantic embeddings are generated and persisted within a high-performance vector database with hybrid keyword-frequency scoring.

When students pose natural-language queries in English or Hindi, the system performs dense semantic retrieval with strict distance thresholding. Rather than treating ungrounded generation as acceptable, the system incorporates an evidence-sufficiency gate: questions for which official institutional documentation is missing or insufficient trigger an honest refusal rather than speculative generation. Furthermore, the generation pipeline enforces verifiable citation attribution, linking factual policy assertions to exact document titles, page numbers, and excerpt snippets. Beyond question answering, UniMate AI features an automated notice intelligence pipeline that extracts event dates and form deadlines into an academic calendar, an AI study assistant that synthesizes syllabus practice multiple-choice questions (MCQs) with pedagogical explanations, and an administrative dashboard for real-time document indexing and unanswered query gap analysis.

The system was evaluated across benchmark institutional policy sets, achieving 100% test passing efficiency across 19 unit and integration test suites, zero ungrounded policy hallucinations, and reliable cross-lingual retrieval. The entire end-to-end platform is containerized via Docker and deployed live in production on cloud infrastructure, demonstrating a scalable, verifiable, and student-centric paradigm for automated higher education academic governance.

**IEEE Keywords—** Retrieval-Augmented Generation (RAG), Natural Language Processing (NLP), Large Language Models (LLMs), University Academic Governance, Document Intelligence, Vector Database, Grounded Generation, Multilingual Conversational Agent, Dayananda Sagar University.
