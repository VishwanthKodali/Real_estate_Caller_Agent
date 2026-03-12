from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.app.database.models import ProjectType, ProjectStatus


class ProjectCreate(BaseModel):
    name: str
    location: Optional[str] = None
    project_type: ProjectType = ProjectType.APARTMENT
    total_units: Optional[int] = None
    price_range_min: Optional[float] = None
    price_range_max: Optional[float] = None
    possession_date: Optional[str] = None
    rera_id: Optional[str] = None
    amenities: Optional[str] = None
    status: ProjectStatus = ProjectStatus.UNDER_CONSTRUCTION
    description: Optional[str] = None

class ProjectUpdate(ProjectCreate):
    name: Optional[str] = None

class ProjectOut(BaseModel):
    id: int
    owner_id: int
    name: str
    location: Optional[str]
    project_type: ProjectType
    total_units: Optional[int]
    price_range_min: Optional[float]
    price_range_max: Optional[float]
    possession_date: Optional[str]
    rera_id: Optional[str]
    amenities: Optional[str]
    status: ProjectStatus
    description: Optional[str]
    elevenlabs_agent_id: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True