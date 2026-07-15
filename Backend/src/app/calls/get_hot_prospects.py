from sqlalchemy.orm import Session

from src.app.database.models import Call, CallOutcome, Prospect
from src.app.calls.helpers import get_campaign_or_404


class GetHotProspectsRequest:

    def list(db: Session, user, campaign_id: int):
        """Get high-interest prospects (interested or site visit requested)."""
        get_campaign_or_404(campaign_id, user, db)

        hot_calls = db.query(Call).filter(
            Call.campaign_id == campaign_id,
            Call.outcome.in_(
                [CallOutcome.SITE_VISIT_REQUESTED, CallOutcome.INTERESTED]
            ),
        ).all()

        result = []
        for call in hot_calls:
            prospect = db.query(Prospect).filter(
                Prospect.id == call.prospect_id
            ).first()
            if prospect:
                result.append(
                    {
                        "call_id": call.id,
                        "prospect": {
                            "id": prospect.id,
                            "name": prospect.name,
                            "phone": prospect.phone,
                            "email": prospect.email,
                            "status": prospect.status,
                        },
                        "outcome": call.outcome,
                        "interest_level": call.interest_level,
                        "duration_seconds": call.duration_seconds,
                        "called_at": call.created_at,
                    }
                )

        return result


get_hot_prospects_service = GetHotProspectsRequest
