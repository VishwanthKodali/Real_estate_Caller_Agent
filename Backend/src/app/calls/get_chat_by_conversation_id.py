import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.app.database.models import Call, Campaign, Prospect, CallOutcome, ProspectStatus
from src.app.calls.helpers import parse_transcript, update_prospect_status_from_outcome

logger = logging.getLogger(__name__)


class GetChatByConversationIdRequest:

    async def get(
        db: Session,
        user,
        conversation_id: str,
        elevenlabs_service,
    ):
        """Get call transcript and chat history by conversation ID."""
        call = db.query(Call).filter(
            Call.elevenlabs_conversation_id == conversation_id
        ).first()
        if not call:
            raise HTTPException(
                status_code=404, detail="No call found for this conversation_id"
            )

        campaign = db.query(Campaign).filter(
            Campaign.id == call.campaign_id,
            Campaign.owner_id == user.id,
        ).first()
        if not campaign:
            raise HTTPException(status_code=403, detail="Not authorized")

        prospect = db.query(Prospect).filter(Prospect.id == call.prospect_id).first()

        messages = parse_transcript(call.transcript)

        # Fetch from ElevenLabs if transcript not in DB
        if not messages:
            try:
                logger.info(f"Fetching transcript from ElevenLabs: {conversation_id}")
                data = await elevenlabs_service.get_conversation(conversation_id)
                raw = (
                    data.get("transcript")
                    or data.get("messages")
                    or data.get("conversation", {}).get("transcript")
                    or []
                )
                if isinstance(raw, list) and raw:
                    messages = [
                        {
                            "role": msg.get("role") or msg.get("speaker", "agent"),
                            "message": msg.get("message")
                            or msg.get("text")
                            or msg.get("content", ""),
                            "time_in_call_secs": msg.get("time_in_call_secs")
                            or msg.get("timestamp"),
                        }
                        for msg in raw
                        if isinstance(msg, dict)
                    ]
                    call.transcript = parse_transcript(messages)  # Store normalized
                    duration = (
                        data.get("metadata", {}).get("call_duration_secs")
                        or data.get("duration_seconds")
                        or 0
                    )
                    if duration and not call.duration_seconds:
                        call.duration_seconds = int(duration)
                    db.commit()
            except Exception as e:
                logger.error(f"Failed to fetch transcript from ElevenLabs: {e}")

        # Run intent analysis if outcome unknown
        outcome_is_unset = (
            call.outcome is None
            or call.outcome == CallOutcome.UNKNOWN
            or str(call.outcome).lower() in ("unknown", "calloutcome.unknown", "none")
        )

        if messages and outcome_is_unset:
            transcript_text = " ".join(
                msg.get("message") or msg.get("text") or "" for msg in messages
            )
            logger.info(f"Running intent analysis on {len(transcript_text)} chars")
            intent = elevenlabs_service.analyze_transcript_for_intent(transcript_text)
            outcome_val = intent["outcome"]
            logger.info(f"Intent result: {intent}")

            try:
                call.outcome = CallOutcome(outcome_val)
                call.interest_level = intent["interest_level"]
            except ValueError:
                logger.warning(f"Unknown outcome value: {outcome_val}")

            if prospect:
                update_prospect_status_from_outcome(db, prospect, call.outcome)

            db.commit()
            logger.info(
                f"Saved outcome={call.outcome}, interest_level={call.interest_level}"
            )

        return {
            "call_id": call.id,
            "campaign_id": call.campaign_id,
            "conversation_id": conversation_id,
            "prospect_name": prospect.name if prospect else None,
            "prospect_phone": prospect.phone if prospect else None,
            "duration_seconds": call.duration_seconds,
            "status": call.status,
            "outcome": call.outcome,
            "interest_level": call.interest_level,
            "notes": call.notes,
            "created_at": call.created_at,
            "message_count": len(messages),
            "messages": messages,
        }


get_chat_service = GetChatByConversationIdRequest
