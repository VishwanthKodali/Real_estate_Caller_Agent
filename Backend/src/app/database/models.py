from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from src.app.database.db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    company_name = Column(String(255))
    phone = Column(String(20))
    rera_number = Column(String(100))
    office_address = Column(Text)
    website = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    projects = relationship("Project", back_populates="owner")
    campaigns = relationship("Campaign", back_populates="owner")


class ProjectType(str, enum.Enum):
    APARTMENT = "apartment"
    VILLA = "villa"
    PLOT = "plot"
    COMMERCIAL = "commercial"


class ProjectStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    UNDER_CONSTRUCTION = "under_construction"
    READY_TO_MOVE = "ready_to_move"


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    location = Column(String(500))
    project_type = Column(SAEnum(ProjectType), default=ProjectType.APARTMENT)
    total_units = Column(Integer)
    price_range_min = Column(Float)
    price_range_max = Column(Float)
    possession_date = Column(String(100))
    rera_id = Column(String(100))
    amenities = Column(Text)  # JSON string
    status = Column(SAEnum(ProjectStatus), default=ProjectStatus.UNDER_CONSTRUCTION)
    description = Column(Text)
    elevenlabs_agent_id = Column(String(255))  # ElevenLabs agent linked to this project
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="projects")
    documents = relationship("Document", back_populates="project")
    campaigns = relationship("Campaign", back_populates="project")


class DocumentType(str, enum.Enum):
    BROCHURE = "brochure"
    FLOOR_PLAN = "floor_plan"
    PRICE_LIST = "price_list"
    AMENITY_DETAILS = "amenity_details"
    LOCATION_MAP = "location_map"
    PAYMENT_PLAN = "payment_plan"
    OTHER = "other"


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500))
    file_path = Column(String(1000))
    file_type = Column(String(50))  # pdf, docx, image
    doc_type = Column(SAEnum(DocumentType), default=DocumentType.BROCHURE)
    extracted_text = Column(Text)  # Gemini 1.5 Flash extracted content
    elevenlabs_kb_doc_id = Column(String(255))  # ElevenLabs knowledge base document ID
    processing_status = Column(String(50), default="pending")  # pending, processing, done, failed
    file_size = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="documents")


class CampaignType(str, enum.Enum):
    LAUNCH = "launch"
    OFFER = "offer"
    FOLLOW_UP = "follow_up"
    SITE_VISIT = "site_visit"


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    campaign_type = Column(SAEnum(CampaignType), default=CampaignType.LAUNCH)
    status = Column(SAEnum(CampaignStatus), default=CampaignStatus.DRAFT)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    elevenlabs_agent_id = Column(String(255))
    agent_greeting = Column(Text)
    agent_system_prompt = Column(Text)
    voice_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="campaigns")
    project = relationship("Project", back_populates="campaigns")
    prospects = relationship("Prospect", back_populates="campaign")
    calls = relationship("Call", back_populates="campaign")


class ProspectStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"
    SITE_VISIT_SCHEDULED = "site_visit_scheduled"
    CONVERTED = "converted"


class Prospect(Base):
    __tablename__ = "prospects"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    name = Column(String(255))
    phone = Column(String(20), nullable=False)
    email = Column(String(255))
    budget_min = Column(Float)
    budget_max = Column(Float)
    preferred_unit_type = Column(String(100))  # 1BHK, 2BHK, etc.
    preferred_location = Column(String(255))
    source = Column(String(100))  # website, walk-in, referral
    status = Column(SAEnum(ProspectStatus), default=ProspectStatus.NEW)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    campaign = relationship("Campaign", back_populates="prospects")
    calls = relationship("Call", back_populates="prospect")


class CallStatus(str, enum.Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_ANSWER = "no_answer"
    BUSY = "busy"


class CallOutcome(str, enum.Enum):
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"
    SITE_VISIT_REQUESTED = "site_visit_requested"
    CALLBACK_REQUESTED = "callback_requested"
    NO_ANSWER = "no_answer"
    VOICEMAIL = "voicemail"
    UNKNOWN = "unknown"


class Call(Base):
    __tablename__ = "calls"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    prospect_id = Column(Integer, ForeignKey("prospects.id"), nullable=False)
    elevenlabs_conversation_id = Column(String(255))
    status = Column(SAEnum(CallStatus), default=CallStatus.QUEUED)
    outcome = Column(SAEnum(CallOutcome), default=CallOutcome.UNKNOWN)
    duration_seconds = Column(Integer)
    transcript = Column(Text)  # Full conversation transcript JSON
    interest_level = Column(Integer)  # 1-5 score
    notes = Column(Text)
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    campaign = relationship("Campaign", back_populates="calls")
    prospect = relationship("Prospect", back_populates="calls")
