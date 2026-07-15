import logging
from sqlalchemy.orm import Session
from src.app.database.models import Call, Prospect
from src.app.campaigns.helpers import get_campaign_or_404

logger = logging.getLogger(__name__)


class DeleteCampaignRequest:

    async def delete(db: Session, user, campaign_id: int, elevenlabs_service):
        """Delete a campaign and related resources."""
        campaign = get_campaign_or_404(campaign_id, user, db)

        # Delete calls and prospects first
        db.query(Call).filter(Call.campaign_id == campaign_id).delete(
            synchronize_session=False
        )
        db.query(Prospect).filter(Prospect.campaign_id == campaign_id).delete(
            synchronize_session=False
        )

        # Delete ElevenLabs agent
        if campaign.elevenlabs_agent_id:
            try:
                await elevenlabs_service.delete_agent(campaign.elevenlabs_agent_id)
            except Exception as e:
                logger.error(f"Failed to delete ElevenLabs agent: {str(e)}")

        db.delete(campaign)
        db.commit()


delete_campaign_service = DeleteCampaignRequest
