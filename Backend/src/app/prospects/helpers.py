from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.app.database.models import Campaign

def get_campaign_or_404(campaign_id: int, user, db: Session) -> Campaign:
    c = db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.owner_id == user.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return c