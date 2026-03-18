from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.app.database.models import ProspectStatus

class ProspectCreate(BaseModel):
    name: Optional[str] = None
    phone: str
    email: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    preferred_unit_type: Optional[str] = None
    preferred_location: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None

class ProspectOut(BaseModel):
    id: int
    campaign_id: int
    name: Optional[str]
    phone: str
    email: Optional[str]
    budget_min: Optional[float]
    budget_max: Optional[float]
    preferred_unit_type: Optional[str]
    preferred_location: Optional[str]
    source: Optional[str]
    status: ProspectStatus
    notes: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True