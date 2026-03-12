from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.app.database.models import Project
from src.app.v1.models.projects import ProjectUpdate


class UpdateProjectRequest:

    def update(db: Session, project_id: int, payload: ProjectUpdate, user):
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.owner_id == user.id,
        ).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        for field, value in payload.dict(exclude_unset=True).items():
            setattr(project, field, value)
        db.commit()
        db.refresh(project)
        return project


update_project_service = UpdateProjectRequest
