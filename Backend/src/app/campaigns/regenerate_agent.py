import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.app.database.models import Project
from src.app.campaigns.helpers import (
    get_campaign_or_404,
    build_system_prompt_with_knowledge,
)

logger = logging.getLogger(__name__)


class RegenerateAgentRequest:

    async def regenerate(db: Session, user, campaign_id: int, elevenlabs_service):
        """Recreate the ElevenLabs agent with latest document knowledge."""
        campaign = get_campaign_or_404(campaign_id, user, db)
        project = db.query(Project).filter(Project.id == campaign.project_id).first()

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Delete old agent
        if campaign.elevenlabs_agent_id:
            try:
                await elevenlabs_service.delete_agent(campaign.elevenlabs_agent_id)
            except Exception as e:
                logger.warning(f"Failed to delete old agent: {str(e)}")

        # Rebuild system prompt with latest docs
        system_prompt = elevenlabs_service.build_real_estate_system_prompt(
            developer_name=user.company_name or user.full_name,
            project_name=project.name,
            project_location=project.location or "our prime location",
            developer_rera=user.rera_number,
        )

        system_prompt = build_system_prompt_with_knowledge(
            system_prompt, project, db
        )

        try:
            agent = await elevenlabs_service.create_agent(
                name=f"{campaign.name} — {project.name}",
                system_prompt=system_prompt,
                first_message=campaign.agent_greeting,
                voice_id=campaign.voice_id or "21m00Tcm4TlvDq8ikWAM",
            )
            campaign.elevenlabs_agent_id = agent.get("agent_id")
            campaign.agent_system_prompt = system_prompt
            db.commit()
            db.refresh(campaign)
        except Exception as e:
            logger.error(f"Agent regeneration failed: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Agent regeneration failed: {str(e)}"
            )

        return campaign


regenerate_agent_service = RegenerateAgentRequest
