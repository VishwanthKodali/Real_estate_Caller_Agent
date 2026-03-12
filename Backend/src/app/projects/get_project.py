from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.app.database.models import Project


class GetProjectRequest:

    def get(db: Session, project_id: int, user):
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.owner_id == user.id,
        ).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project


get_project_service = GetProjectRequest
