import logging
from datetime import datetime
from sqlalchemy.orm import Session

from src.app.database.models import Call, CallStatus, CallOutcome, Prospect
from src.app.calls.helpers import (
    normalize_transcript_messages,
    update_prospect_status_from_outcome,
)

logger = logging.getLogger(__name__)


class ConversationWebhookRequest:

    def handle(db: Session, payload: dict, elevenlabs_service):
        """Handle ElevenLabs post-call webhook."""
        conversation_id = payload.get("conversation_id")
        if not conversation_id:
            return {"status": "ignored"}

        call = db.query(Call).filter(
            Call.elevenlabs_conversation_id == conversation_id
        ).first()
        if not call:
            return {"status": "call not found"}

        raw_transcript = payload.get("transcript", [])
        duration = (
            payload.get("duration_seconds")
            or payload.get("call_duration_secs")
            or 0
        )

        # Save transcript as proper JSON
        call.transcript = normalize_transcript_messages(raw_transcript)
        call.duration_seconds = int(duration) if duration else 0
        call.status = CallStatus.COMPLETED
        call.ended_at = datetime.utcnow()

        # Run intent analysis
        if raw_transcript:
            transcript_text = (
                " ".join(
                    msg.get("message") or msg.get("text") or ""
                    for msg in raw_transcript
                    if isinstance(msg, dict)
                )
                if isinstance(raw_transcript, list)
                else str(raw_transcript)
            )
            try:
                intent = elevenlabs_service.analyze_transcript_for_intent(
                    transcript_text
                )
                outcome_val = intent["outcome"]
                call.outcome = CallOutcome(outcome_val)
                call.interest_level = intent["interest_level"]
            except (ValueError, KeyError, Exception) as e:
                logger.warning(f"Failed to analyze transcript: {e}")

            prospect = db.query(Prospect).filter(
                Prospect.id == call.prospect_id
            ).first()
            if prospect and call.outcome:
                update_prospect_status_from_outcome(db, prospect, call.outcome)

        db.commit()
        return {"status": "ok"}


conversation_webhook_service = ConversationWebhookRequest
