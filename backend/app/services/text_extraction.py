import os
from typing import List, Dict, Any, Tuple
import fitz  # PyMuPDF
from docx import Document as DocxDocument

class ExtractedPage:
    def __init__(self, page_number: int, text: str):
        self.page_number = page_number
        self.text = text

class TextExtractionService:
    @staticmethod
    def extract_from_pdf(file_path: str) -> Tuple[List[ExtractedPage], Dict[str, Any]]:
        """
        Extracts text page-by-page from a PDF using PyMuPDF (fitz).
        Preserves page numbering (1-indexed) and collects page metadata.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        doc = fitz.open(file_path)
        pages: List[ExtractedPage] = []
        empty_pages = 0

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_text = page.get_text("text").strip()
            
            if not page_text:
                empty_pages += 1
                page_text = f"[Empty or image-only page]"
            
            pages.append(ExtractedPage(page_number=page_idx + 1, text=page_text))

        metadata = {
            "page_count": len(doc),
            "empty_pages": empty_pages,
            "title": doc.metadata.get("title") or os.path.basename(file_path),
            "author": doc.metadata.get("author") or "University Admin",
            "format": "PDF"
        }
        doc.close()
        return pages, metadata

    @staticmethod
    def extract_from_docx(file_path: str) -> Tuple[List[ExtractedPage], Dict[str, Any]]:
        """
        Extracts text from a DOCX file using python-docx.
        Since DOCX does not have native physical page breaks,
        we group paragraphs into logical semantic sections/pages (~1500 chars).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        doc = DocxDocument(file_path)
        full_text_blocks = []

        # Extract paragraphs
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                full_text_blocks.append(text)

        # Extract table contents
        for table in doc.tables:
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    full_text_blocks.append(" | ".join(row_cells))

        # Partition into simulated pages (~1500 characters per page)
        pages: List[ExtractedPage] = []
        current_chunk = []
        current_len = 0
        page_num = 1

        for block in full_text_blocks:
            current_chunk.append(block)
            current_len += len(block)
            if current_len >= 1400:
                pages.append(ExtractedPage(page_number=page_num, text="\n\n".join(current_chunk)))
                current_chunk = []
                current_len = 0
                page_num += 1

        if current_chunk or not pages:
            pages.append(ExtractedPage(page_number=page_num, text="\n\n".join(current_chunk) if current_chunk else "[Empty document]"))

        metadata = {
            "page_count": len(pages),
            "empty_pages": 0,
            "title": os.path.basename(file_path),
            "author": "University Admin",
            "format": "DOCX"
        }
        return pages, metadata

    @classmethod
    def extract(cls, file_path: str, file_type: str) -> Tuple[List[ExtractedPage], Dict[str, Any]]:
        file_type = file_type.lower().strip()
        if file_type.endswith("pdf") or file_path.lower().endswith(".pdf"):
            return cls.extract_from_pdf(file_path)
        elif file_type.endswith("docx") or file_path.lower().endswith(".docx"):
            return cls.extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}. Supported types: PDF, DOCX")
