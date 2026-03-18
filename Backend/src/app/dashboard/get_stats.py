from sqlalchemy.orm import Session
from src.app.database.models import Campaign, Project, Prospect, Call, CallStatus, CallOutcome, CampaignStatus

class GetDashboardStatsService:
    @staticmethod
    def get_stats(db: Session, user):
        # projects/campaign counts
        total_projects = db.query(Project).filter(Project.owner_id == user.id).count()
        total_campaigns = db.query(Campaign).filter(Campaign.owner_id == user.id).count()
        active_campaigns = db.query(Campaign).filter(
            Campaign.owner_id == user.id, Campaign.status == CampaignStatus.ACTIVE
        ).count()

        # gather campaign ids owned by user
        campaign_ids = [c.id for c in db.query(Campaign.id).filter(Campaign.owner_id == user.id).all()]
        if campaign_ids:
            total_prospects = db.query(Prospect).filter(Prospect.campaign_id.in_(campaign_ids)).count()
            total_calls = db.query(Call).filter(Call.campaign_id.in_(campaign_ids)).count()
            completed_calls = db.query(Call).filter(
                Call.campaign_id.in_(campaign_ids), Call.status == CallStatus.COMPLETED
            ).count()
            site_visits = db.query(Call).filter(
                Call.campaign_id.in_(campaign_ids), Call.outcome == CallOutcome.SITE_VISIT_REQUESTED
            ).count()
            interested = db.query(Call).filter(
                Call.campaign_id.in_(campaign_ids), Call.outcome == CallOutcome.INTERESTED
            ).count()
            recent_calls = db.query(Call).filter(Call.campaign_id.in_(campaign_ids)).order_by(Call.created_at.desc()).limit(10).all()
        else:
            total_prospects = total_calls = completed_calls = site_visits = interested = 0
            recent_calls = []

        conversion_rate = round((site_visits / completed_calls * 100), 2) if completed_calls > 0 else 0

        recent_activity = []
        for call in recent_calls:
            prospect = db.query(Prospect).filter(Prospect.id == call.prospect_id).first()
            campaign = db.query(Campaign).filter(Campaign.id == call.campaign_id).first()
            recent_activity.append({
                "call_id": call.id,
                "prospect_name": prospect.name if prospect else "Unknown",
                "prospect_phone": prospect.phone if prospect else "",
                "campaign_name": campaign.name if campaign else "",
                "status": call.status,
                "outcome": call.outcome,
                "created_at": call.created_at,
            })

        return {
            "overview": {
                "total_projects": total_projects,
                "total_campaigns": total_campaigns,
                "active_campaigns": active_campaigns,
                "total_prospects": total_prospects,
                "total_calls": total_calls,
                "completed_calls": completed_calls,
                "site_visits_requested": site_visits,
                "interested_prospects": interested,
                "conversion_rate": conversion_rate,
            },
            "recent_activity": recent_activity,
        }