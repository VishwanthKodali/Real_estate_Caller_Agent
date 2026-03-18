from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.app.database.models import Call, CallStatus, Prospect
from src.app.calls.helpers import get_campaign_or_404


class CallSingleProspectRequest:

    def initiate(
        db: Session,
        user,
        campaign_id: int,
        prospect_id: int,
        background_tasks=None,
        make_single_call_func=None,
    ):
        """Create a call for a single prospect and queue it."""
        campaign = get_campaign_or_404(campaign_id, user, db)

        prospect = db.query(Prospect).filter(
            Prospect.id == prospect_id,
            Prospect.campaign_id == campaign_id,
        ).first()
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospect not found")

        call = Call(
            campaign_id=campaign_id,
            prospect_id=prospect_id,
            status=CallStatus.QUEUED,
        )
        db.add(call)
        db.commit()
        db.refresh(call)

        if background_tasks and make_single_call_func:
            background_tasks.add_task(make_single_call_func, call.id)

        return call


call_single_prospect_service = CallSingleProspectRequest
