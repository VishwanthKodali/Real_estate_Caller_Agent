from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.app.database.models import Project
from src.app.v1.models.projects import ProjectCreate


class CreateProjectRequest:

    def create(db: Session, user, payload: ProjectCreate):
        project = Project(owner_id=user.id, **payload.dict())
        db.add(project)
        db.commit()
        db.refresh(project)
        return project


create_project_service = CreateProjectRequest
