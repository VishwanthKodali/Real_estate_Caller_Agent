import json
import logging
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session, sessionmaker

from src.app.database.models import Campaign, Call, Prospect, ProspectStatus, CallStatus, CallOutcome

logger = logging.getLogger(__name__)


def get_campaign_or_404(campaign_id: int, user, db: Session) -> Campaign:
    """Verify user owns the campaign."""
    logger.debug(f"get_campaign_or_404 campaign_id={campaign_id} user={getattr(user,'id',None)}")
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.owner_id == user.id
    ).first()
    if not campaign:
        logger.warning(f"campaign {campaign_id} not found for user {user.id}")
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


def get_call_or_404(call_id: int, campaign_id: int, db: Session) -> Call:
    """Get a call for a specific campaign."""
    logger.debug(f"get_call_or_404 call_id={call_id} campaign_id={campaign_id}")
    call = db.query(Call).filter(
        Call.id == call_id,
        Call.campaign_id == campaign_id
    ).first()
    if not call:
        logger.warning(f"call {call_id} not found in campaign {campaign_id}")
        raise HTTPException(status_code=404, detail="Call not found")
    return call


def parse_transcript(transcript) -> list:
    """Parse stored transcript JSON into a clean list of chat messages."""
    logger.debug(f"parse_transcript input={transcript}")
    if not transcript:
        return []
    try:
        parsed = json.loads(transcript) if isinstance(transcript, str) else transcript
        if isinstance(parsed, list):
            return [
                {
                    "role": msg.get("role", "agent"),
                    "message": msg.get("message") or msg.get("text") or "",
                    "time_in_call_secs": msg.get("time_in_call_secs"),
                }
                for msg in parsed if isinstance(msg, dict)
            ]
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"parse_transcript failed: {e}")
        return [{"role": "agent", "message": str(transcript), "time_in_call_secs": None}]
    return []


def normalize_transcript_messages(raw_transcript) -> str:
    """Convert raw transcript to JSON array string."""
    logger.debug(f"normalize_transcript_messages input={raw_transcript}")
    if isinstance(raw_transcript, list):
        normalised = [
            {
                "role": msg.get("role") or msg.get("speaker", "agent"),
                "message": msg.get("message") or msg.get("text") or msg.get("content", ""),
                "time_in_call_secs": msg.get("time_in_call_secs") or msg.get("timestamp"),
            }
            for msg in raw_transcript if isinstance(msg, dict)
        ]
        return json.dumps(normalised)
    elif isinstance(raw_transcript, str):
        return json.dumps([{"role": "agent", "message": raw_transcript, "time_in_call_secs": None}])
    else:
        return json.dumps([])


def update_prospect_status_from_outcome(db: Session, prospect: Prospect, outcome: CallOutcome):
    """Update prospect status based on call outcome."""
    logger.info(f"update_prospect_status_from_outcome prospect_id={prospect.id} outcome={outcome}")
    if outcome == CallOutcome.SITE_VISIT_REQUESTED:
        prospect.status = ProspectStatus.SITE_VISIT_SCHEDULED
    elif outcome == CallOutcome.INTERESTED:
        prospect.status = ProspectStatus.INTERESTED
    elif outcome == CallOutcome.NOT_INTERESTED:
        prospect.status = ProspectStatus.NOT_INTERESTED
