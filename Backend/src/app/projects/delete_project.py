from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.app.database.models import Project


class DeleteProjectRequest:

    def delete(db: Session, project_id: int, user):
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.owner_id == user.id,
        ).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # import related models lazily to avoid circular references
        from src.app.database.models import Campaign, Document, Prospect, Call

        # Get all campaign IDs for this project
        campaign_ids = [c.id for c in db.query(Campaign.id).filter(Campaign.project_id == project_id).all()]

        if campaign_ids:
            db.query(Call).filter(Call.campaign_id.in_(campaign_ids)).delete(synchronize_session=False)
            db.query(Prospect).filter(Prospect.campaign_id.in_(campaign_ids)).delete(synchronize_session=False)
            db.query(Campaign).filter(Campaign.project_id == project_id).delete(synchronize_session=False)

        db.query(Document).filter(Document.project_id == project_id).delete(synchronize_session=False)

        db.delete(project)
        db.commit()



delete_project_service = DeleteProjectRequest
