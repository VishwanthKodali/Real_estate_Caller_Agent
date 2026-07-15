from typing import Optional
from sqlalchemy.orm import Session
from src.app.database.models import Campaign


class ListCampaignsRequest:

    def list(db: Session, user, project_id: Optional[int] = None):
        """List campaigns for current user, optionally filtered by project."""
        q = db.query(Campaign).filter(Campaign.owner_id == user.id)
        if project_id:
            q = q.filter(Campaign.project_id == project_id)
        return q.order_by(Campaign.id.desc()).all()


list_campaigns_service = ListCampaignsRequest
