from pathlib import Path
import pytest
from backend.app.services.text_extraction import TextExtractionService

SAMPLE_DIR = Path(__file__).resolve().parents[2] / "data" / "sample_docs"

def test_extract_pdf_pages_and_metadata():
    pdf_path = SAMPLE_DIR / "academic_regulations_2026.pdf"
    pages, meta = TextExtractionService.extract_from_pdf(str(pdf_path))
    
    assert len(pages) == 3
    assert pages[0].page_number == 1
    assert "Academic Conduct" in pages[0].text or "Regulations" in pages[0].text
    assert pages[1].page_number == 2
    assert "75%" in pages[1].text
    assert "Condonation" in pages[1].text
    assert meta["page_count"] == 3

def test_extract_docx_paragraphs():
    docx_path = SAMPLE_DIR / "hostel_and_mess_regulations_2026.docx"
    pages, meta = TextExtractionService.extract_from_docx(str(docx_path))
    
    assert len(pages) >= 1
    combined = " ".join([p.text for p in pages])
    assert "Mess Fee" in combined
    assert "9:30 PM" in combined
