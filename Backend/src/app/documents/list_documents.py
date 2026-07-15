from sqlalchemy.orm import Session
from src.app.database.models import Document
from src.app.documents.helpers import get_project_or_404


class ListDocumentsRequest:

    def list(db: Session, user, project_id: int):
        """List all documents for a project."""
        get_project_or_404(project_id, user, db)
        return db.query(Document).filter(Document.project_id == project_id).all()


list_documents_service = ListDocumentsRequest
