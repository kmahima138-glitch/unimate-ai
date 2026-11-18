import re
from typing import List, Dict, Any, Tuple
from backend.app.services.embeddings import embedding_service
from backend.app.services.vector_store import vector_store
from backend.app.core.config import settings

# Academic domain cross-lingual query expansion for Hindi/Hinglish
HINDI_ACADEMIC_MAP = {
    "उपस्थिति": "attendance",
    "हाजिरी": "attendance",
    "परीक्षा": "examination exam",
    "इम्तिहान": "exam",
    "न्यूनतम": "minimum",
    "नियम": "regulation rules",
    "शुल्क": "fees fee",
    "फीस": "fees fee",
    "छात्रावास": "hostel",
    "हॉस्टल": "hostel",
    "मेस": "mess fee",
    "प्रवेश": "admission",
    "परिणाम": "result grade",
    "पुनर्मूल्यांकन": "revaluation",
    "अंतिम तिथि": "deadline date",
    "समय सीमा": "deadline",
    "छात्रवृत्ति": "scholarship",
    "पाठ्यक्रम": "syllabus course",
    "हॉल टिकट": "hall ticket admit card",
    "प्रवेश पत्र": "admit card hall ticket"
}

GENERIC_TERMS = {
    "what", "is", "the", "of", "and", "in", "to", "a", "for", "on", "with", "as", "by", "at", 
    "an", "this", "that", "are", "be", "from", "university", "policy", "student", "students", 
    "rules", "tell", "me", "about", "can", "you", "does", "have"
}

class RetrievalService:
    def __init__(self):
        self.top_k = settings.TOP_K_RETRIEVAL
        self.threshold = 0.38

    def _expand_query(self, query: str) -> str:
        """Expands Hindi academic keywords with English synonyms to bridge cross-lingual gap."""
        expanded = query
        for hi_term, en_term in HINDI_ACADEMIC_MAP.items():
            if hi_term in query:
                expanded += f" {en_term}"
        return expanded

    def retrieve(self, query: str, category: str = None) -> Tuple[List[Dict[str, Any]], str, bool]:
        """
        Retrieves relevant document chunks for a query.
        Returns:
            - chunks: list of retrieved chunk dictionaries
            - evidence_level: 'strong' | 'partial' | 'insufficient'
            - has_conflict: boolean indicating if contradictory statements were detected
        """
        if not query.strip():
            return [], "insufficient", False

        expanded_query = self._expand_query(query)
        query_emb = embedding_service.embed_text(expanded_query)
        
        chunks = vector_store.search(
            query_embedding=query_emb,
            query_text=expanded_query,
            top_k=self.top_k,
            min_score=self.threshold,
            category=category
        )

        if not chunks:
            return [], "insufficient", False

        # Topic relevance guardrail:
        # Check whether distinctive topical query tokens appear in retrieved text
        content_tokens = [
            w.lower() for w in re.findall(r"[\w]+", expanded_query) 
            if w.lower() not in GENERIC_TERMS and len(w) > 3
        ]
        
        if content_tokens:
            combined_chunk_text = " ".join([c["text"].lower() for c in chunks])
            matching_content_tokens = sum(1 for t in content_tokens if t in combined_chunk_text)
            if matching_content_tokens == 0:
                return [], "insufficient", False

        top_score = chunks[0]["similarity_score"]
        
        # Evidence evaluation
        if top_score >= 0.52:
            evidence_level = "strong"
        elif top_score >= self.threshold:
            evidence_level = "partial"
        else:
            evidence_level = "insufficient"

        # Check for conflicts between distinct documents
        has_conflict = self._detect_conflicts(chunks)

        return chunks, evidence_level, has_conflict

    def _detect_conflicts(self, chunks: List[Dict[str, Any]]) -> bool:
        """
        Inspects chunks from multiple documents to detect conflicting numerical rules
        such as attendance thresholds, fee amounts, or dates.
        """
        if len(chunks) < 2:
            return False

        # Group by document
        doc_texts: Dict[str, str] = {}
        for c in chunks:
            doc_id = c["document_id"]
            doc_texts[doc_id] = doc_texts.get(doc_id, "") + " " + c["text"]

        if len(doc_texts) < 2:
            return False

        percentages = []
        for text in doc_texts.values():
            pcts = re.findall(r"(\d{2})%", text)
            if pcts:
                percentages.append(set(pcts))

        if len(percentages) >= 2 and percentages[0] != percentages[1]:
            return True

        return False

retrieval_service = RetrievalService()
