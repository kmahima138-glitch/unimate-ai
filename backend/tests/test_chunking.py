import pytest
from backend.app.services.chunking import ChunkingService
from backend.app.services.text_extraction import ExtractedPage

def test_chunking_preserves_page_numbers_and_metadata():
    chunker = ChunkingService(chunk_size=200, chunk_overlap=40)
    pages = [
        ExtractedPage(page_number=1, text="This is page one content. " * 15),
        ExtractedPage(page_number=2, text="This is page two content containing rules. " * 15)
    ]
    
    chunks = chunker.chunk_document("doc_test_123", pages, {"title": "Test Doc"})
    assert len(chunks) > 2
    
    # Check that chunks from page 1 have page_number 1
    page1_chunks = [c for c in chunks if c.page_number == 1]
    page2_chunks = [c for c in chunks if c.page_number == 2]
    
    assert len(page1_chunks) >= 1
    assert len(page2_chunks) >= 1
    assert all("doc_test_123" in c.chunk_id for c in chunks)
    assert all(c.document_id == "doc_test_123" for c in chunks)

def test_chunking_overlap():
    chunker = ChunkingService(chunk_size=100, chunk_overlap=30)
    text = "First section detailing policy A. Second section detailing policy B. Third section detailing policy C."
    parts = chunker.split_text_recursive(text, 50, 20)
    assert len(parts) >= 2
