from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    company_name: str
    username: str
    password: str
    rera_number: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[str] = None
    office_address: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    role: str = "admin"  # Default role is 'agent', can be 'admin' or 'agent'

class Project(SQLModel, table=True):
    __tablename__ = "projects"
    id: Optional[int] = Field(default=None, primary_key=True)
    developer_id: int = Field(foreign_key="users.id")
    name: str
    location: str
    project_type: Optional[str] = None  # apartment, villa, plot, etc.
    total_units: Optional[int] = None
    price_range: Optional[str] = None
    possession_date: Optional[datetime] = None
    rera_id: Optional[str] = None
    key_amenities: Optional[str] = None
    status: str = "draft"  # draft, active, completed, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Campaign(SQLModel, table=True):
    __tablename__ = "campaigns"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    name: str
    ai_voice_id: str
    ai_agent_config: Optional[str] = Field(default=None) # Prompt or setup string
    status: str = "draft" # draft, active, completed
    created_at: datetime = Field(default_factory=datetime.utcnow)

