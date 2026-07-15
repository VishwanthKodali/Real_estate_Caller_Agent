from sqlalchemy.orm import Session

from src.app.database.models import Call, Prospect
from src.app.calls.helpers import get_campaign_or_404


class GetCampaignStatsRequest:

    def stats(db: Session, user, campaign_id: int):
        """Get aggregated stats for a campaign."""
        get_campaign_or_404(campaign_id, user, db)

        all_calls = db.query(Call).filter(Call.campaign_id == campaign_id).all()
        prospects = db.query(Prospect).filter(Prospect.campaign_id == campaign_id).all()

        total_calls = len(all_calls)
        total_prospects = len(prospects)
        completed = sum(
            1
            for c in all_calls
            if str(c.status).lower() in ("completed", "callstatus.completed")
        )
        failed = sum(
            1 for c in all_calls if str(c.status).lower() in ("failed", "callstatus.failed")
        )
        answered = sum(
            1 for c in all_calls if c.transcript and len(c.transcript) > 10
        )
        not_answered = completed - answered if completed > answered else 0
        interested = sum(
            1
            for c in all_calls
            if str(c.outcome).lower() in ("interested", "calloutcome.interested")
        )
        not_interested = sum(
            1
            for c in all_calls
            if str(c.outcome).lower()
            in ("not_interested", "calloutcome.not_interested")
        )
        site_visit = sum(
            1
            for c in all_calls
            if str(c.outcome).lower()
            in ("site_visit_requested", "calloutcome.site_visit_requested")
        )
        callback = sum(
            1
            for c in all_calls
            if str(c.outcome).lower()
            in ("callback_requested", "calloutcome.callback_requested")
        )
        unknown = sum(
            1
            for c in all_calls
            if str(c.outcome).lower() in ("unknown", "calloutcome.unknown", "none")
            or c.outcome is None
        )
        conversion_rate = (
            round((site_visit / total_calls * 100) if total_calls > 0 else 0, 2)
        )

        return {
            "total_prospects": total_prospects,
            "total_calls": total_calls,
            "completed_calls": completed,
            "failed_calls": failed,
            "answered": answered,
            "not_answered": not_answered,
            "interested": interested,
            "not_interested": not_interested,
            "site_visit_requested": site_visit,
            "callback_requested": callback,
            "unknown_outcome": unknown,
            "conversion_rate": conversion_rate,
        }


get_campaign_stats_service = GetCampaignStatsRequest
