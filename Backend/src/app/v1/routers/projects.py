import logging
from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from src.app.database.db import get_db
from src.app.database.models import User
from src.app.v1.models.projects import ProjectCreate, ProjectUpdate, ProjectOut
from src.app.auth import get_current_user
from src.app.projects import (
    create_project_service,
    list_projects_service,
    get_project_service,
    update_project_service,
    delete_project_service,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"create_project called by user={user.id}")
    return create_project_service.create(db, user, payload)


@router.get("", response_model=List[ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"list_projects called by user={user.id}")
    return list_projects_service.list(db, user)


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"get_project called project_id={project_id} user={user.id}")
    return get_project_service.get(db, project_id, user)


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"update_project called project_id={project_id} user={user.id}")
    return update_project_service.update(db, project_id, payload, user)


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"delete_project called project_id={project_id} user={user.id}")
    return delete_project_service.delete(db, project_id, user)
