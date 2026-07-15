from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.app.database.models import Document
from src.app.documents.helpers import get_project_or_404


class GetDocumentTextRequest:

    def get_text(db: Session, user, project_id: int, doc_id: int):
        """Get extracted text and processing status for a document."""
        get_project_or_404(project_id, user, db)
        doc = db.query(Document).filter(
            Document.id == doc_id,
            Document.project_id == project_id
        ).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return {
            "extracted_text": doc.extracted_text,
            "processing_status": doc.processing_status,
        }


get_document_text_service = GetDocumentTextRequest
