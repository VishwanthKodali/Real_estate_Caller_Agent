import logging
from sqlalchemy.orm import Session

from src.app.database.models import Call, CallOutcome, Prospect
from src.app.calls.helpers import (
    get_campaign_or_404,
    parse_transcript,
    update_prospect_status_from_outcome,
)

logger = logging.getLogger(__name__)


class RefreshAllOutcomesRequest:

    def refresh(db: Session, user, campaign_id: int, elevenlabs_service):
        """Re-run intent analysis on all calls with transcripts but no outcome."""
        get_campaign_or_404(campaign_id, user, db)

        calls = db.query(Call).filter(
            Call.campaign_id == campaign_id,
            Call.transcript.isnot(None),
        ).all()

        updated = 0
        for call in calls:
            outcome_str = str(call.outcome).lower()
            already_set = outcome_str not in (
                "none",
                "unknown",
                "calloutcome.unknown",
            )
            if already_set:
                continue

            messages = parse_transcript(call.transcript)
            if not messages:
                continue

            transcript_text = " ".join(m.get("message") or "" for m in messages)
            if not transcript_text.strip():
                continue

            intent = elevenlabs_service.analyze_transcript_for_intent(transcript_text)
            outcome_val = intent["outcome"]
            try:
                call.outcome = CallOutcome(outcome_val)
                call.interest_level = intent["interest_level"]
            except ValueError:
                logger.warning(f"Unknown outcome value: {outcome_val}")
                continue

            prospect = db.query(Prospect).filter(Prospect.id == call.prospect_id).first()
            if prospect:
                update_prospect_status_from_outcome(db, prospect, call.outcome)

            updated += 1

        db.commit()
        logger.info(
            f"refresh-outcomes: updated {updated} calls for campaign {campaign_id}"
        )
        return {
            "updated": updated,
            "message": f"Refreshed outcomes for {updated} call(s)",
        }


refresh_all_outcomes_service = RefreshAllOutcomesRequest
