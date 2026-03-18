import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.app.database.models import Campaign, Project, Document

logger = logging.getLogger(__name__)


def get_campaign_or_404(campaign_id: int, user, db: Session) -> Campaign:
    """Verify user owns the campaign."""
    logger.debug(f"get_campaign_or_404 campaign_id={campaign_id} user={getattr(user,'id',None)}")
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.owner_id == user.id
    ).first()
    if not campaign:
        logger.warning(f"campaign {campaign_id} not found for user {user.id}")
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


def get_project_or_404(project_id: int, user, db: Session) -> Project:
    """Verify user owns the project."""
    logger.debug(f"get_project_or_404 project_id={project_id} user={getattr(user,'id',None)}")
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id
    ).first()
    if not project:
        logger.warning(f"project {project_id} not found for user {user.id}")
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def build_system_prompt_with_knowledge(
    base_prompt: str,
    project: Project,
    db: Session,
) -> str:
    """
    Inject extracted document text into system prompt.
    Workaround for ElevenLabs free tier (no KB support).
    """
    logger.debug(f"build_system_prompt_with_knowledge project_id={project.id}")
    project_docs = db.query(Document).filter(
        Document.project_id == project.id,
        Document.processing_status == "done",
        Document.extracted_text.isnot(None),
    ).all()

    if project_docs:
        knowledge_sections = []
        for doc in project_docs:
            if doc.extracted_text and doc.extracted_text.strip():
                knowledge_sections.append(
                    f"=== {doc.original_filename} ({doc.doc_type.replace('_', ' ').title()}) ===\n{doc.extracted_text}"
                )

        if knowledge_sections:
            knowledge_text = "\n\n".join(knowledge_sections)
            # Limit to 12000 chars to stay within ElevenLabs prompt limits
            if len(knowledge_text) > 12000:
                knowledge_text = knowledge_text[:12000] + "\n\n[Additional document content truncated]"

            base_prompt += f"\n\n{'='*60}\nPROJECT KNOWLEDGE BASE\n{'='*60}\nAnswer ALL prospect questions using ONLY the following information:\n\n{knowledge_text}"

    return base_prompt
