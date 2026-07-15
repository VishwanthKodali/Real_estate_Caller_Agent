from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.app.database.models import Prospect
from src.app.v1.models.prospect import ProspectCreate

class UpdateProspectService:
    @staticmethod
    def update_prospect(campaign_id: int, prospect_id: int, payload: ProspectCreate, db: Session, user):
        from .helpers import get_campaign_or_404
        get_campaign_or_404(campaign_id, user, db)
        p = db.query(Prospect).filter(Prospect.id == prospect_id, Prospect.campaign_id == campaign_id).first()
        if not p:
            raise HTTPException(status_code=404, detail="Prospect not found")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(p, field, value)
        db.commit()
        db.refresh(p)
        return p