from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.app.database.models import Document
from src.app.documents.helpers import get_project_or_404


class GetDocumentRequest:

    def get(db: Session, user, project_id: int, doc_id: int):
        """Get a single document by ID."""
        get_project_or_404(project_id, user, db)
        doc = db.query(Document).filter(
            Document.id == doc_id,
            Document.project_id == project_id
        ).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc


get_document_service = GetDocumentRequest
