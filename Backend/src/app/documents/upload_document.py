import os
import uuid
import logging
from pathlib import Path
from typing import Optional
from fastapi import HTTPException, BackgroundTasks, UploadFile
from sqlalchemy.orm import Session, sessionmaker

from src.app.database.models import Document, DocumentType
from src.app.documents.helpers import get_project_or_404, process_document_background
from src.app.common import Settings

logger = logging.getLogger(__name__)

ALLOWED_TYPES = {"pdf", "docx", "doc", "png", "jpg", "jpeg", "gif", "webp", "bmp", "txt"}


class UploadDocumentRequest:

    async def upload(
        db: Session,
        user,
        project_id: int,
        file: UploadFile,
        doc_type: DocumentType,
        background_tasks: BackgroundTasks,
        SessionLocal: sessionmaker,
    ):
        """Upload a document and queue background extraction."""
        get_project_or_404(project_id, user, db)

        ext = Path(file.filename).suffix.lower().strip(".")
        if ext not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{ext}' not allowed. Allowed: {', '.join(ALLOWED_TYPES)}"
            )

        content = await file.read()
        file_size = len(content)

        if file_size > Settings.max_file_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max {Settings.max_file_size_mb}MB"
            )

        unique_name = f"{uuid.uuid4().hex}_{file.filename}"
        upload_dir = Path(Settings.upload_dir) / str(project_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / unique_name

        with open(file_path, "wb") as f:
            f.write(content)

        doc = Document(
            project_id=project_id,
            filename=unique_name,
            original_filename=file.filename,
            file_path=str(file_path),
            file_type=ext,
            doc_type=doc_type,
            file_size=file_size,
            processing_status="pending",
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        background_tasks.add_task(process_document_background, doc.id, SessionLocal)
        return doc


upload_document_service = UploadDocumentRequest
