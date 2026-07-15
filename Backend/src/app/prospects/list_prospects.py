from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
from src.app.database.models import Prospect, ProspectStatus

class ListProspectsService:
    @staticmethod
    def list_prospects(campaign_id: int, status: Optional[ProspectStatus], db: Session, user):
        from .helpers import get_campaign_or_404
        get_campaign_or_404(campaign_id, user, db)
        q = db.query(Prospect).filter(Prospect.campaign_id == campaign_id)
        if status:
            q = q.filter(Prospect.status == status)
        return q.all()