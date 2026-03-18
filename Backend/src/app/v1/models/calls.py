from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.app.database.models import CallStatus, CallOutcome

class CallOut(BaseModel):
    id: int
    campaign_id: int
    prospect_id: int
    elevenlabs_conversation_id: Optional[str]
    status: CallStatus
    outcome: CallOutcome
    duration_seconds: Optional[int]
    transcript: Optional[str]
    interest_level: Optional[int]
    notes: Optional[str]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    created_at: datetime
    class Config:
        from_attributes = True

class CampaignStats(BaseModel):
    total_prospects: int
    total_calls: int
    completed_calls: int
    failed_calls: int
    interested: int
    not_interested: int
    site_visit_requested: int
    conversion_rate: float