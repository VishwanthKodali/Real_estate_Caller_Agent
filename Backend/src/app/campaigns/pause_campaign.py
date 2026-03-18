from sqlalchemy.orm import Session
from src.app.database.models import CampaignStatus
from src.app.campaigns.helpers import get_campaign_or_404


class PauseCampaignRequest:

    def pause(db: Session, user, campaign_id: int):
        """Pause a campaign."""
        campaign = get_campaign_or_404(campaign_id, user, db)
        campaign.status = CampaignStatus.PAUSED
        db.commit()
        db.refresh(campaign)
        return campaign


pause_campaign_service = PauseCampaignRequest
