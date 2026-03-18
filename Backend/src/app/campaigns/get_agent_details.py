import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.app.campaigns.helpers import get_campaign_or_404

logger = logging.getLogger(__name__)


class GetAgentDetailsRequest:

    async def get_details(db: Session, user, campaign_id: int, elevenlabs_service):
        """Get ElevenLabs agent details for a campaign."""
        campaign = get_campaign_or_404(campaign_id, user, db)
        if not campaign.elevenlabs_agent_id:
            raise HTTPException(
                status_code=404,
                detail="No ElevenLabs agent for this campaign. Recreate the campaign to generate one.",
            )
        try:
            return await elevenlabs_service.get_agent(campaign.elevenlabs_agent_id)
        except Exception as e:
            logger.error(f"Failed to fetch agent details: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


get_agent_details_service = GetAgentDetailsRequest
