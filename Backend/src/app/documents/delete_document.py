import os
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.app.database.models import Document
from src.app.documents.helpers import get_project_or_404


class DeleteDocumentRequest:

    def delete(db: Session, user, project_id: int, doc_id: int):
        """Delete a document and its file from storage."""
        get_project_or_404(project_id, user, db)
        doc = db.query(Document).filter(
            Document.id == doc_id,
            Document.project_id == project_id
        ).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.file_path and os.path.exists(doc.file_path):
            os.remove(doc.file_path)

        db.delete(doc)
        db.commit()


delete_document_service = DeleteDocumentRequest
