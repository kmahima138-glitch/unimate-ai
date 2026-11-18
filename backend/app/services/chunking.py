import re
from typing import List, Dict, Any
from backend.app.services.text_extraction import ExtractedPage
from backend.app.core.config import settings

class Chunk:
    def __init__(self, chunk_id: str, document_id: str, chunk_index: int, page_number: int, text: str, metadata: Dict[str, Any] = None):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.chunk_index = chunk_index
        self.page_number = page_number
        self.text = text
        self.metadata = metadata or {}

class ChunkingService:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def split_text_recursive(self, text: str, max_size: int, overlap: int) -> List[str]:
        """
        Recursively splits text using paragraph, sentence, and word boundaries.
        Ensures resulting chunks are around max_size characters with given overlap.
        """
        text = text.strip()
        if not text:
            return []
        if len(text) <= max_size:
            return [text]

        # Splitting delimiters in priority order
        separators = ["\n\n", "\n", ". ", "; ", ", ", " "]
        
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + max_size
            if end >= text_len:
                chunks.append(text[start:].strip())
                break

            # Find best split point near end
            split_pos = -1
            search_window = text[start:end + 1]
            
            for sep in separators:
                last_sep = search_window.rfind(sep)
                if last_sep != -1 and last_sep > (max_size // 3):
                    split_pos = start + last_sep + len(sep)
                    break
            
            if split_pos == -1 or split_pos <= start:
                split_pos = end

            chunk_text = text[start:split_pos].strip()
            if chunk_text:
                chunks.append(chunk_text)

            # Advance start pointer considering overlap
            start = max(start + 1, split_pos - overlap)

        return chunks

    def chunk_document(self, document_id: str, pages: List[ExtractedPage], doc_metadata: Dict[str, Any] = None) -> List[Chunk]:
        """
        Takes extracted pages and produces sequential chunks preserving page numbers.
        """
        all_chunks: List[Chunk] = []
        chunk_idx = 0

        for page in pages:
            page_text = page.text.strip()
            if not page_text or page_text == "[Empty or image-only page]":
                continue

            page_chunks = self.split_text_recursive(page_text, self.chunk_size, self.chunk_overlap)
            
            for p_chunk in page_chunks:
                chunk_id = f"{document_id}_p{page.page_number}_c{chunk_idx}"
                meta = {
                    **(doc_metadata or {}),
                    "page_number": page.page_number,
                    "chunk_index": chunk_idx,
                    "char_count": len(p_chunk)
                }
                chunk = Chunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    chunk_index=chunk_idx,
                    page_number=page.page_number,
                    text=p_chunk,
                    metadata=meta
                )
                all_chunks.append(chunk)
                chunk_idx += 1

        return all_chunks
