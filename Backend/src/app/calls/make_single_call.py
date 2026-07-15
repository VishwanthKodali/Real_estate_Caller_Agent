import logging
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from src.app.database.models import Call, Campaign, Prospect, ProspectStatus, CallStatus

logger = logging.getLogger(__name__)


async def make_single_call(call_id: int, SessionLocal: sessionmaker, elevenlabs_service):
    """Background task: initiate outbound call via ElevenLabs."""
    db = SessionLocal()
    try:
        call = db.query(Call).filter(Call.id == call_id).first()
        if not call:
            logger.warning(f"Call {call_id} not found")
            return

        campaign = db.query(Campaign).filter(Campaign.id == call.campaign_id).first()
        prospect = db.query(Prospect).filter(Prospect.id == call.prospect_id).first()

        if not campaign or not prospect:
            call.status = CallStatus.FAILED
            call.notes = "Missing campaign or prospect data"
            db.commit()
            logger.error(f"Missing campaign or prospect for call {call_id}")
            return

        if not campaign.elevenlabs_agent_id:
            call.status = CallStatus.FAILED
            call.notes = "No ElevenLabs agent configured. Go to campaign and click 'Regenerate Agent'."
            call.ended_at = datetime.utcnow()
            db.commit()
            logger.warning(f"No agent configured for campaign {campaign.id}")
            return

        try:
            call.status = CallStatus.IN_PROGRESS
            call.started_at = datetime.utcnow()
            db.commit()

            result = await elevenlabs_service.initiate_outbound_call(
                agent_id=campaign.elevenlabs_agent_id,
                to_number=prospect.phone,
            )

            conversation_id = result.get("conversation_id") or result.get("callSid")
            call.elevenlabs_conversation_id = conversation_id
            call.status = CallStatus.COMPLETED
            call.ended_at = datetime.utcnow()
            prospect.status = ProspectStatus.CONTACTED
            db.commit()
            logger.info(f"Call {call_id} completed with conversation_id {conversation_id}")

        except Exception as e:
            call.status = CallStatus.FAILED
            call.notes = str(e)
            call.ended_at = datetime.utcnow()
            db.commit()
            logger.error(f"Call {call_id} failed: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error in make_single_call: {str(e)}")
    finally:
        db.close()
