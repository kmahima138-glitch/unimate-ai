from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class DocumentChunkSchema(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    text: str
    page_number: int
    metadata: Optional[Dict[str, Any]] = None

class DocumentResponse(BaseModel):
    id: str
    title: str
    filename: str
    category: str
    file_type: str
    file_size: int
    page_count: int
    status: str
    error_message: Optional[str] = None
    chunk_count: int
    uploaded_by: str
    uploaded_at: str
    version: int

class DocumentUploadResponse(BaseModel):
    document: DocumentResponse
    message: str

class DocumentStatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    categories: Dict[str, int]
    status_summary: Dict[str, int]
