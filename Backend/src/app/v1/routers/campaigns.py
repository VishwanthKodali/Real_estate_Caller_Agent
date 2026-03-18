import logging
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.app.database.db import get_db
from src.app.database.models import User
from src.app.v1.models.campaigns import CampaignCreate, CampaignUpdate, CampaignOut
from src.app.auth import get_current_user
from src.app.services import eleven_labs_service
from src.app.campaigns import (
    create_campaign_service,
    list_campaigns_service,
    get_campaign_service,
    update_campaign_service,
    delete_campaign_service,
    activate_campaign_service,
    pause_campaign_service,
    get_agent_details_service,
    regenerate_agent_service,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.post("", response_model=CampaignOut, status_code=201)
async def create_campaign(
    payload: CampaignCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"create_campaign called by user={user.id}")
    return await create_campaign_service.create(
        db, user, payload, eleven_labs_service
    )


@router.get("", response_model=List[CampaignOut])
def list_campaigns(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"list_campaigns called by user={user.id} project_id={project_id}")
    return list_campaigns_service.list(db, user, project_id)


@router.get("/{campaign_id}", response_model=CampaignOut)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"get_campaign called campaign_id={campaign_id} user={user.id}")
    return get_campaign_service.get(db, user, campaign_id)


@router.put("/{campaign_id}", response_model=CampaignOut)
async def update_campaign(
    campaign_id: int,
    payload: CampaignUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"update_campaign called campaign_id={campaign_id} user={user.id}")
    return update_campaign_service.update(db, user, campaign_id, payload)


@router.delete("/{campaign_id}", status_code=204)
async def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"delete_campaign called campaign_id={campaign_id} user={user.id}")
    return await delete_campaign_service.delete(
        db, user, campaign_id, eleven_labs_service
    )


@router.post("/{campaign_id}/activate", response_model=CampaignOut)
def activate_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"activate_campaign called campaign_id={campaign_id} user={user.id}")
    return activate_campaign_service.activate(db, user, campaign_id)


@router.post("/{campaign_id}/pause", response_model=CampaignOut)
def pause_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"pause_campaign called campaign_id={campaign_id} user={user.id}")
    return pause_campaign_service.pause(db, user, campaign_id)


@router.get("/{campaign_id}/agent-details")
async def get_agent_details(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"get_agent_details called campaign_id={campaign_id} user={user.id}")
    return await get_agent_details_service.get_details(
        db, user, campaign_id, eleven_labs_service
    )


@router.post("/{campaign_id}/regenerate-agent", response_model=CampaignOut)
async def regenerate_agent(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"regenerate_agent called campaign_id={campaign_id} user={user.id}")
    return await regenerate_agent_service.regenerate(
        db, user, campaign_id, eleven_labs_service
    )
