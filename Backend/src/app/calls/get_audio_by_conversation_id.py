import logging
from fastapi import HTTPException, Response
from sqlalchemy.orm import Session

from src.app.database.models import Call, Campaign, Prospect, CallOutcome, ProspectStatus
from src.app.calls.helpers import parse_transcript, update_prospect_status_from_outcome

logger = logging.getLogger(__name__)


class GetAudioByConversationIdRequest:

    async def get(
        db: Session,
        user,
        conversation_id: str,
        el,
    ):
        call = db.query(Call).filter(Call.elevenlabs_conversation_id == conversation_id).first()
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")

        campaign = db.query(Campaign).filter(
            Campaign.id == call.campaign_id,
            Campaign.owner_id == user.id
        ).first()
        if not campaign:
            raise HTTPException(status_code=403, detail="Not authorized")

        try:
            audio_bytes = await el.get_conversation_audio(conversation_id)
            return Response(
                content=audio_bytes,
                media_type="audio/mpeg",
                headers={"Content-Disposition": f"inline; filename=call_{conversation_id}.mp3"}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not fetch audio: {str(e)}")
        
get_audio_service= GetAudioByConversationIdRequest