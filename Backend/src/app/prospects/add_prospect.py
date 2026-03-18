from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.app.database.models import Prospect
from src.app.v1.models.prospect import ProspectCreate

class AddProspectService:
    @staticmethod
    def add_prospect(campaign_id: int, payload: ProspectCreate, db: Session, user):
        from .helpers import get_campaign_or_404
        get_campaign_or_404(campaign_id, user, db)

        existing = db.query(Prospect).filter(
            Prospect.campaign_id == campaign_id,
            Prospect.phone == payload.phone
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Prospect with this phone already exists in campaign")

        prospect = Prospect(campaign_id=campaign_id, **payload.model_dump())
        db.add(prospect)
        db.commit()
        db.refresh(prospect)
        return prospect