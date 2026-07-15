from sqlalchemy.orm import Session
from src.app.database.models import Project


class ListProjectsRequest:

    def list(db: Session, user):
        return db.query(Project).filter(Project.owner_id == user.id).all()


list_projects_service = ListProjectsRequest
