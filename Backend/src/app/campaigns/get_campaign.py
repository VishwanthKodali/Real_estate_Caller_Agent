from sqlalchemy.orm import Session
from src.app.campaigns.helpers import get_campaign_or_404


class GetCampaignRequest:

    def get(db: Session, user, campaign_id: int):
        """Get a single campaign by ID."""
        return get_campaign_or_404(campaign_id, user, db)


get_campaign_service = GetCampaignRequest
