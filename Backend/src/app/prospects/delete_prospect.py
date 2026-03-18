from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.app.database.models import Prospect

class DeleteProspectService:
    @staticmethod
    def delete_prospect(campaign_id: int, prospect_id: int, db: Session, user):
        from .helpers import get_campaign_or_404
        get_campaign_or_404(campaign_id, user, db)
        p = db.query(Prospect).filter(Prospect.id == prospect_id, Prospect.campaign_id == campaign_id).first()
        if not p:
            raise HTTPException(status_code=404, detail="Prospect not found")

        # Delete linked calls first to avoid FK constraint violation
        from src.app.database.models import Call
        db.query(Call).filter(Call.prospect_id == prospect_id).delete(synchronize_session=False)

        db.delete(p)
        db.commit()