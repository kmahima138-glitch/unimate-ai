import re
import json
from typing import List, Dict, Any, Optional
from backend.app.db.database import db
from backend.app.services.vector_store import vector_store
from backend.app.services.embeddings import embedding_service
from backend.app.services.llm_service import llm_service

class StudyService:
    def generate_quiz(self, topic: str = "University Syllabus", document_id: Optional[str] = None, num_questions: int = 4) -> Dict[str, Any]:
        """
        Generates practice multiple-choice questions with answer keys and explanations
        from indexed study materials or documents.
        """
        chunks = []
        if document_id:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT text, page_number FROM document_chunks WHERE document_id = ? LIMIT 6", (document_id,))
                chunks = [{"text": r["text"], "page_number": r["page_number"], "document_title": "Selected Document"} for r in cursor.fetchall()]
        
        if not chunks:
            # Query vector store for topic
            q_emb = embedding_service.embed_text(topic)
            chunks = vector_store.search(q_emb, query_text=topic, top_k=4)

        source_doc_title = chunks[0]["document_title"] if chunks else "University Course Material"
        combined_text = "\n".join([c["text"] for c in chunks]) if chunks else topic

        # Try generating via Gemini if API key available
        if llm_service._client:
            prompt = f"""
Based ONLY on the following university study material, generate {num_questions} high-quality Multiple Choice Questions (MCQs) for student practice.
Return ONLY valid JSON matching this exact structure:
[
  {{
    "id": 1,
    "question": "Question text...",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_option_index": 0,
    "explanation": "Clear explanation grounded in the text...",
    "source_reference": "{source_doc_title}"
  }}
]

STUDY MATERIAL:
{combined_text[:2500]}
"""
            try:
                res = llm_service._client.models.generate_content(
                    model=llm_service.model_name,
                    contents=prompt
                )
                if res and res.text:
                    clean_json = re.sub(r"^```json\s*|\s*```$", "", res.text.strip(), flags=re.MULTILINE)
                    parsed_mcqs = json.loads(clean_json)
                    return {
                        "topic": topic,
                        "document_title": source_doc_title,
                        "questions": parsed_mcqs,
                        "disclaimer": "These practice questions are generated for revision and do not represent official university examination papers."
                    }
            except Exception:
                pass

        # Robust, grounded deterministic practice question generator
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", combined_text) if len(s.strip()) > 35]
        questions = []
        
        for i in range(min(num_questions, len(sentences))):
            s = sentences[i]
            # Formulate question around sentence
            words = [w for w in re.findall(r"\w+", s) if len(w) > 4 and w.lower() not in ["university", "student", "course", "following"]]
            key_term = words[0] if words else "Regulation"
            
            q_text = f"According to the university material, what is the primary purpose or requirement regarding {key_term}?"
            correct_ans = s[:120] + ("..." if len(s) > 120 else "")
            
            options = [
                correct_ans,
                f"It is discretionary and decided only by external examiners without documentation.",
                f"It was superseded by national recommendations and is no longer evaluated.",
                f"It applies only to postgraduate doctorate scholars in semester 8."
            ]
            
            questions.append({
                "id": i + 1,
                "question": q_text,
                "options": options,
                "correct_option_index": 0,
                "explanation": f"Explicitly stated in {source_doc_title}: '{s[:180]}...'",
                "source_reference": f"{source_doc_title}"
            })

        if not questions:
            questions.append({
                "id": 1,
                "question": "What is the standard university protocol regarding course attendance requirements?",
                "options": [
                    "Students must maintain minimum mandatory attendance as outlined in regulations.",
                    "Attendance is voluntary for all laboratory sessions.",
                    "Attendance can be waived without medical certification.",
                    "Attendance is recorded only in the final examination week."
                ],
                "correct_option_index": 0,
                "explanation": "Official academic regulations mandate attendance verification for examination eligibility.",
                "source_reference": source_doc_title
            })

        return {
            "topic": topic,
            "document_title": source_doc_title,
            "questions": questions,
            "disclaimer": "These practice questions are generated for revision and do not represent official university examination papers."
        }

    def generate_flashcards(self, topic: str = "Key Concepts", document_id: Optional[str] = None) -> Dict[str, Any]:
        """Generates conceptual flashcards for quick revision."""
        quiz_data = self.generate_quiz(topic, document_id, num_questions=4)
        cards = []
        for q in quiz_data["questions"]:
            cards.append({
                "id": q["id"],
                "front": q["question"],
                "back": q["options"][q["correct_option_index"]] + "\n\n💡 " + q["explanation"],
                "category": topic
            })
        return {
            "topic": topic,
            "document_title": quiz_data["document_title"],
            "flashcards": cards
        }

study_service = StudyService()
