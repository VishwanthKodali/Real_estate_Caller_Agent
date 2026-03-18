import logging
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional

from src.app.database.db import get_db
from src.app.auth.security import get_current_user
from src.app.v1.models.prospect import ProspectCreate, ProspectOut
from src.app.database.models import ProspectStatus
from src.app.prospects import (
    AddProspectService,
    ListProspectsService,
    UpdateProspectService,
    GetProspectService,
    BulkUploadProspectsService,
    DeleteProspectService,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/prospects", tags=["Prospects"])


@router.post("/{campaign_id}", response_model=ProspectOut, status_code=201)
def add_prospect(
    campaign_id: int, payload: ProspectCreate,
    db: Session = Depends(get_db), user = Depends(get_current_user)
):
    logger.info(f"add_prospect called campaign_id={campaign_id}")
    return AddProspectService.add_prospect(campaign_id, payload, db, user)


@router.post("/{campaign_id}/bulk-upload")
async def bulk_upload_prospects(
    campaign_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    logger.info(f"bulk_upload_prospects called campaign_id={campaign_id}")
    """
    Upload CSV with columns:
    name, phone, email, budget_min, budget_max, preferred_unit_type, preferred_location, source, notes
    Phone is required. All others optional.
    """
    content = await file.read()
    return BulkUploadProspectsService.bulk_upload_prospects(campaign_id, content, db, user)


@router.get("/{campaign_id}", response_model=List[ProspectOut])
def list_prospects(
    campaign_id: int,
    status: Optional[ProspectStatus] = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    logger.info(f"list_prospects called campaign_id={campaign_id} status={status}")
    return ListProspectsService.list_prospects(campaign_id, status, db, user)


@router.get("/{campaign_id}/{prospect_id}", response_model=ProspectOut)
def get_prospect(
    campaign_id: int, prospect_id: int,
    db: Session = Depends(get_db), user = Depends(get_current_user)
):
    logger.info(f"get_prospect called campaign_id={campaign_id} prospect_id={prospect_id}")
    return GetProspectService.get_prospect(campaign_id, prospect_id, db, user)


@router.put("/{campaign_id}/{prospect_id}", response_model=ProspectOut)
def update_prospect(
    campaign_id: int, prospect_id: int, payload: ProspectCreate,
    db: Session = Depends(get_db), user = Depends(get_current_user)
):
    logger.info(f"update_prospect called campaign_id={campaign_id} prospect_id={prospect_id}")
    return UpdateProspectService.update_prospect(campaign_id, prospect_id, payload, db, user)


@router.delete("/{campaign_id}/{prospect_id}", status_code=204)
def delete_prospect(
    campaign_id: int, prospect_id: int,
    db: Session = Depends(get_db), user = Depends(get_current_user)
):
    logger.info(f"delete_prospect called campaign_id={campaign_id} prospect_id={prospect_id}")
    DeleteProspectService.delete_prospect(campaign_id, prospect_id, db, user)