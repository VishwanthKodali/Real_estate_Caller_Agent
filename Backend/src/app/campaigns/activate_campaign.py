from sqlalchemy.orm import Session
from src.app.database.models import CampaignStatus
from src.app.campaigns.helpers import get_campaign_or_404


class ActivateCampaignRequest:

    def activate(db: Session, user, campaign_id: int):
        """Activate a campaign."""
        campaign = get_campaign_or_404(campaign_id, user, db)
        campaign.status = CampaignStatus.ACTIVE
        db.commit()
        db.refresh(campaign)
        return campaign


activate_campaign_service = ActivateCampaignRequest
