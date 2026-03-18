from fastapi import HTTPException, BackgroundTasks
from sqlalchemy.orm import Session, sessionmaker
from src.app.database.models import Document
from src.app.documents.helpers import get_project_or_404, process_document_background


class ReprocessDocumentRequest:

    def reprocess(
        db: Session,
        user,
        project_id: int,
        doc_id: int,
        background_tasks: BackgroundTasks,
        SessionLocal: sessionmaker,
    ):
        """Requeue document for background text extraction."""
        get_project_or_404(project_id, user, db)
        doc = db.query(Document).filter(
            Document.id == doc_id,
            Document.project_id == project_id
        ).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        doc.processing_status = "pending"
        db.commit()
        background_tasks.add_task(process_document_background, doc.id, SessionLocal)
        return {"message": "Reprocessing started"}


reprocess_document_service = ReprocessDocumentRequest
