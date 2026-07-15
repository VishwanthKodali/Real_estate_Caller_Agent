from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.app.database.models import DocumentType

class DocumentOut(BaseModel):
    id: int
    project_id: int
    filename: str
    original_filename: Optional[str]
    file_type: Optional[str]
    doc_type: DocumentType
    processing_status: str
    elevenlabs_kb_doc_id: Optional[str]
    file_size: Optional[int]
    created_at: datetime
    class Config:
        from_attributes = True