from typing import Optional
from sqlalchemy.orm import Session

from src.app.database.models import Call, CallStatus, CallOutcome
from src.app.calls.helpers import get_campaign_or_404


class GetCallLogsRequest:

    def list(
        db: Session,
        user,
        campaign_id: int,
        status: Optional[CallStatus] = None,
        outcome: Optional[CallOutcome] = None,
    ):
        """Get call logs for a campaign with optional filtering."""
        get_campaign_or_404(campaign_id, user, db)

        q = db.query(Call).filter(Call.campaign_id == campaign_id)
        if status:
            q = q.filter(Call.status == status)
        if outcome:
            q = q.filter(Call.outcome == outcome)

        return q.order_by(Call.created_at.desc()).all()


get_call_logs_service = GetCallLogsRequest
