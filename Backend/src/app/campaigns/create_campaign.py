import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.app.database.models import Campaign
from src.app.v1.models.campaigns import CampaignCreate
from src.app.campaigns.helpers import (
    get_project_or_404,
    build_system_prompt_with_knowledge,
)

logger = logging.getLogger(__name__)


class CreateCampaignRequest:

    async def create(db: Session, user, payload: CampaignCreate, elevenlabs_service):
        """Create a new campaign with ElevenLabs agent."""
        project = get_project_or_404(payload.project_id, user, db)

        # Build base system prompt
        system_prompt = (
            payload.agent_system_prompt
            or elevenlabs_service.build_real_estate_system_prompt(
                developer_name=user.company_name or user.full_name,
                project_name=project.name,
                project_location=project.location or "our prime location",
                developer_rera=user.rera_number,
            )
        )

        # Inject document knowledge
        system_prompt = build_system_prompt_with_knowledge(
            system_prompt, project, db
        )

        greeting = payload.agent_greeting or (
            f"Hello! I'm calling from {user.company_name or user.full_name} "
            f"regarding our project {project.name}. Do you have a couple of minutes to learn about it?"
        )

        # Create real ElevenLabs agent (works on free tier)
        agent_id = None
        try:
            agent = await elevenlabs_service.create_agent(
                name=f"{payload.name} — {project.name}",
                system_prompt=system_prompt,
                first_message=greeting,
                voice_id=payload.voice_id or "21m00Tcm4TlvDq8ikWAM",
            )
            agent_id = agent.get("agent_id")
            if agent_id:
                logger.info(f"ElevenLabs agent created: {agent_id}")
            else:
                logger.warning("Agent creation returned no agent_id")
        except Exception as e:
            logger.error(f"ElevenLabs agent creation failed: {str(e)}")

        campaign = Campaign(
            owner_id=user.id,
            project_id=payload.project_id,
            name=payload.name,
            campaign_type=payload.campaign_type,
            start_date=payload.start_date,
            end_date=payload.end_date,
            agent_greeting=greeting,
            agent_system_prompt=system_prompt,
            voice_id=payload.voice_id,
            elevenlabs_agent_id=agent_id,
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return campaign


create_campaign_service = CreateCampaignRequest
