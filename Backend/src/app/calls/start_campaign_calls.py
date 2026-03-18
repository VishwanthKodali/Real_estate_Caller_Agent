import logging
from datetime import datetime
from fastapi import HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from src.app.database.models import Call, CallStatus, Campaign, CampaignStatus, Prospect
from src.app.calls.helpers import get_campaign_or_404

logger = logging.getLogger(__name__)


class StartCampaignCallsRequest:

    def start(
        db: Session,
        user,
        campaign_id: int,
        max_calls=None,
        background_tasks=None,
        make_single_call_func=None,
    ):
        """Queue prospects for outbound calls."""
        campaign = get_campaign_or_404(campaign_id, user, db)

        if campaign.status == CampaignStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Campaign is already completed")

        already_running = db.query(Call).filter(
            Call.campaign_id == campaign_id,
            Call.status.in_([CallStatus.QUEUED, CallStatus.IN_PROGRESS]),
        ).count()

        if already_running > 0:
            raise HTTPException(
                status_code=400,
                detail=f"{already_running} call(s) already queued or in progress.",
            )

        called_ids = db.query(Call.prospect_id).filter(
            Call.campaign_id == campaign_id,
            Call.status.in_([CallStatus.COMPLETED, CallStatus.IN_PROGRESS, CallStatus.QUEUED]),
        ).subquery()

        query = db.query(Prospect).filter(
            Prospect.campaign_id == campaign_id,
            ~Prospect.id.in_(called_ids),
        )
        if max_calls:
            query = query.limit(max_calls)

        pending = query.all()
        if not pending:
            return {"message": "No pending prospects to call", "queued": 0}

        queued = 0
        for prospect in pending:
            call = Call(
                campaign_id=campaign_id,
                prospect_id=prospect.id,
                status=CallStatus.QUEUED,
            )
            db.add(call)
            db.flush()
            if background_tasks and make_single_call_func:
                background_tasks.add_task(make_single_call_func, call.id)
            queued += 1

        campaign.status = CampaignStatus.ACTIVE
        db.commit()
        return {"message": f"Queued {queued} call(s)", "queued": queued}


start_campaign_calls_service = StartCampaignCallsRequest
