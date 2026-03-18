from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.app.database.models import Call, CallOutcome, Prospect
from src.app.calls.helpers import (
    get_campaign_or_404,
    get_call_or_404,
    update_prospect_status_from_outcome,
)


class UpdateCallOutcomeRequest:

    def update(
        db: Session,
        user,
        campaign_id: int,
        call_id: int,
        outcome: CallOutcome,
        interest_level: Optional[int] = None,
        notes: Optional[str] = None,
    ):
        """Update call outcome and prospect status."""
        get_campaign_or_404(campaign_id, user, db)
        call = get_call_or_404(call_id, campaign_id, db)

        call.outcome = outcome
        if interest_level is not None:
            call.interest_level = interest_level
        if notes:
            call.notes = notes

        prospect = db.query(Prospect).filter(Prospect.id == call.prospect_id).first()
        if prospect:
            update_prospect_status_from_outcome(db, prospect, outcome)

        db.commit()
        return {"message": "Updated successfully"}


update_call_outcome_service = UpdateCallOutcomeRequest
