import re
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.app.db.database import db

class NoticeService:
    def extract_and_publish_notice(
        self,
        title: str,
        content: str,
        document_id: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extracts key dates, department, semester, and action requirements from notice text.
        Registers the notice and associated calendar events in the database.
        """
        # Determine category if not explicitly given
        lower_text = (title + " " + content).lower()
        if not category or category == "general":
            if any(k in lower_text for k in ["exam", "hall ticket", "revaluation", "admit card", "timetable"]):
                category = "examination"
            elif any(k in lower_text for k in ["fee", "dues", "tuition", "fine", "refund"]):
                category = "fees"
            elif any(k in lower_text for k in ["scholarship", "financial aid", "fellowship", "merit"]):
                category = "scholarship"
            elif any(k in lower_text for k in ["admission", "seat", "counseling", "lateral entry"]):
                category = "admission"
            elif any(k in lower_text for k in ["placement", "interview", "campus drive", "internship"]):
                category = "placement"
            elif any(k in lower_text for k in ["sports", "fest", "symposium", "holiday", "workshop"]):
                category = "events"
            else:
                category = "general"

        # Extract deadlines / dates prioritized by deadline indicator terms
        date_patterns = [
            r"(?:on or before|before|by|deadline:?|last date:?|due date:?)\s+(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]+\d{4})",
            r"(?:on or before|before|by|deadline:?|last date:?|due date:?)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4})",
            r"\b(?:\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]+\d{4})\b",
            r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{4})\b",
            r"\b(?:before|by|deadline:?)\s+([A-Za-z0-9,\s]{5,25})\b"
        ]
        
        extracted_deadline = None
        for pat in date_patterns:
            matches = re.findall(pat, content, re.IGNORECASE)
            if matches:
                matched_val = matches[0]
                if isinstance(matched_val, tuple):
                    matched_val = [m for m in matched_val if m][0]
                extracted_deadline = str(matched_val).strip()
                break

        # Extract Department
        dept_match = re.search(r"(?:Department of\s+([A-Za-z\s&]+)|Branch:\s*([A-Za-z\s]+)|For\s+([A-Za-z\s]+)\s+Students)", content, re.IGNORECASE)
        affected_dept = "All Departments"
        if dept_match:
            affected_dept = [g for g in dept_match.groups() if g][0].strip()

        # Extract Semester
        sem_match = re.search(r"(?:Semester\s*([0-9IVX]+|all)|([0-9]+(?:st|nd|rd|th)?\s+Semester))", content, re.IGNORECASE)
        affected_sem = sem_match.group(0) if sem_match else "All Semesters"

        # Action item extraction
        action_match = re.search(r"(?:required to\s+([^.\n]+)|action:?\s*([^.\n]+)|must\s+submit\s+([^.\n]+))", content, re.IGNORECASE)
        action_required = [g for g in action_match.groups() if g][0].strip() if action_match else "Review notice and verify eligibility."

        # Summary generation
        summary_sentences = [s.strip() for s in re.split(r"[.\n]", content) if len(s.strip()) > 20]
        summary = ". ".join(summary_sentences[:3]) + "." if summary_sentences else content[:200]

        notice_id = f"not_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow().isoformat()

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO notices (
                id, document_id, title, category, summary, affected_dept,
                affected_semester, action_required, deadline, published_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (notice_id, document_id, title, category, summary, affected_dept, affected_sem, action_required, extracted_deadline, now))

            # If a deadline was found, automatically add it to Academic Events
            if extracted_deadline:
                event_id = f"evt_{uuid.uuid4().hex[:12]}"
                cursor.execute("""
                INSERT INTO academic_events (
                    id, title, event_date, event_type, audience, source_document_id, source_page
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (event_id, f"{title} (Deadline)", extracted_deadline, category, affected_dept, document_id, 1))

            conn.commit()

        return {
            "id": notice_id,
            "document_id": document_id,
            "title": title,
            "category": category,
            "summary": summary,
            "affected_dept": affected_dept,
            "affected_semester": affected_sem,
            "action_required": action_required,
            "deadline": extracted_deadline,
            "published_at": now
        }

    def list_notices(self, category: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM notices WHERE 1=1"
            params = []

            if category and category != "all":
                query += " AND category = ?"
                params.append(category)

            if search:
                query += " AND (title LIKE ? OR summary LIKE ? OR action_required LIKE ?)"
                kw = f"%{search}%"
                params.extend([kw, kw, kw])

            query += " ORDER BY published_at DESC"
            cursor.execute(query, params)
            return [dict(r) for r in cursor.fetchall()]

    def list_academic_events(self) -> List[Dict[str, Any]]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM academic_events ORDER BY event_date ASC")
            return [dict(r) for r in cursor.fetchall()]

notice_service = NoticeService()
