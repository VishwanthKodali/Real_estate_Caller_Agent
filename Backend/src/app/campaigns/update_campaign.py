from sqlalchemy.orm import Session
from src.app.v1.models.campaigns import CampaignUpdate
from src.app.campaigns.helpers import get_campaign_or_404


class UpdateCampaignRequest:

    def update(db: Session, user, campaign_id: int, payload: CampaignUpdate):
        """Update a campaign."""
        campaign = get_campaign_or_404(campaign_id, user, db)
        for field, value in payload.dict(exclude_unset=True).items():
            setattr(campaign, field, value)
        db.commit()
        db.refresh(campaign)
        return campaign


update_campaign_service = UpdateCampaignRequest
