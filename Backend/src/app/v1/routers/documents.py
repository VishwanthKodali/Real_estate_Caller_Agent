import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session

from src.app.database.db import get_db, SessionLocal
from src.app.database.models import User, DocumentType
from src.app.v1.models.documents import DocumentOut
from src.app.auth import get_current_user
from src.app.documents import (
    upload_document_service,
    list_documents_service,
    get_document_service,
    get_document_text_service,
    delete_document_service,
    reprocess_document_service,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/{project_id}/upload", response_model=DocumentOut, status_code=201)
async def upload_document(
    project_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    doc_type: DocumentType = Form(DocumentType.BROCHURE),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"upload_document called project_id={project_id} user={user.id}")
    return await upload_document_service.upload(
        db, user, project_id, file, doc_type, background_tasks, SessionLocal
    )


@router.get("/{project_id}", response_model=List[DocumentOut])
def list_documents(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"list_documents called project_id={project_id} user={user.id}")
    return list_documents_service.list(db, user, project_id)


@router.get("/{project_id}/{doc_id}", response_model=DocumentOut)
def get_document(
    project_id: int,
    doc_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"get_document called project_id={project_id} doc_id={doc_id} user={user.id}")
    return get_document_service.get(db, user, project_id, doc_id)


@router.get("/{project_id}/{doc_id}/text")
def get_document_text(
    project_id: int,
    doc_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"get_document_text called project_id={project_id} doc_id={doc_id} user={user.id}")
    return get_document_text_service.get_text(db, user, project_id, doc_id)


@router.delete("/{project_id}/{doc_id}", status_code=204)
async def delete_document(
    project_id: int,
    doc_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"delete_document.called project_id={project_id} doc_id={doc_id} user={user.id}")
    return delete_document_service.delete(db, user, project_id, doc_id)


@router.post("/{project_id}/reprocess/{doc_id}")
async def reprocess_document(
    project_id: int,
    doc_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"reprocess_document called project_id={project_id} doc_id={doc_id} user={user.id}")
    return reprocess_document_service.reprocess(
        db, user, project_id, doc_id, background_tasks, SessionLocal
    )
