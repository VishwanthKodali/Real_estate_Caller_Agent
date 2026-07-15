import os
import uuid
import logging
from pathlib import Path
from fastapi import HTTPException, BackgroundTasks
from sqlalchemy.orm import Session, sessionmaker

from src.app.database.models import Document, Project
from src.app.services.document_processor import extract_text_from_document
from src.app.common import Settings

logger = logging.getLogger(__name__)


def get_project_or_404(project_id: int, user, db: Session) -> Project:
    """Verify user owns the project."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


async def process_document_background(doc_id: int, SessionLocal: sessionmaker):
    """
    Background task with its own DB session.
    Extracts text via GPT-4o and stores in DB.
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting background processing for document ID: {doc_id}")

        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            logger.warning(f"Document {doc_id} not found")
            return

        doc.processing_status = "processing"
        db.commit()

        logger.info(f"Starting text extraction for document {doc_id}, file: {doc.file_path}")
        try:
            extracted = await extract_text_from_document(doc.file_path, doc.file_type)
            logger.info(f"Text extraction completed for document {doc_id}, extracted length: {len(extracted)}")
        except Exception as e:
            extracted = f"Extraction failed: {str(e)}"
            logger.error(f"Text extraction failed for document {doc_id}: {str(e)}")

        doc.extracted_text = extracted
        doc.elevenlabs_kb_doc_id = None  # No KB on free tier
        doc.processing_status = "done"
        db.commit()
        logger.info(f"Document {doc_id} processing completed successfully")

    except Exception as e:
        logger.error(f"Background processing failed for document {doc_id}: {str(e)}")
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if doc:
                doc.processing_status = "failed"
                doc.extracted_text = f"Processing failed: {str(e)}"
                db.commit()
        except Exception:
            pass
    finally:
        db.close()
        logger.info(f"Closed database session for document {doc_id}")
