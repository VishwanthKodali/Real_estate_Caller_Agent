from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.app.database.models import CampaignType, CampaignStatus

class CampaignCreate(BaseModel):
    project_id: int
    name: str
    campaign_type: CampaignType = CampaignType.LAUNCH
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    agent_greeting: Optional[str] = None
    agent_system_prompt: Optional[str] = None
    voice_id: Optional[str] = None

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    campaign_type: Optional[CampaignType] = None
    status: Optional[CampaignStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    agent_greeting: Optional[str] = None
    agent_system_prompt: Optional[str] = None
    voice_id: Optional[str] = None

class CampaignOut(BaseModel):
    id: int
    owner_id: int
    project_id: int
    name: str
    campaign_type: CampaignType
    status: CampaignStatus
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    elevenlabs_agent_id: Optional[str]
    agent_greeting: Optional[str]
    agent_system_prompt: Optional[str]
    voice_id: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True