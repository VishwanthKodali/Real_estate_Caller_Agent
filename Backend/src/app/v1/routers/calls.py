import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from src.app.database.db import get_db, SessionLocal
from src.app.database.models import User, CallStatus, CallOutcome
from src.app.v1.models.calls import CallOut
from src.app.auth import get_current_user
from src.app.services import eleven_labs_service
from src.app.calls import (
    start_campaign_calls_service,
    call_single_prospect_service,
    get_call_logs_service,
    get_chat_service,
    get_audio_service,
    get_campaign_stats_service,
    refresh_all_outcomes_service,
    update_call_outcome_service,
    get_hot_prospects_service,
    conversation_webhook_service,
    list_voices_service,
    make_single_call,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/calls", tags=["Calls"])


@router.post("/{campaign_id}/start", status_code=202)
async def start_campaign_calls(
    campaign_id: int,
    background_tasks: BackgroundTasks,
    max_calls: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"start_campaign_calls called campaign_id={campaign_id} user={user.id} max_calls={max_calls}")
    return start_campaign_calls_service.start(
        db,
        user,
        campaign_id,
        max_calls,
        background_tasks,
        lambda call_id: make_single_call(call_id, SessionLocal, eleven_labs_service),
    )


@router.post("/{campaign_id}/call/{prospect_id}", response_model=CallOut, status_code=202)
async def call_single_prospect(
    campaign_id: int,
    prospect_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"call_single_prospect called campaign_id={campaign_id} prospect_id={prospect_id} user={user.id}")
    return call_single_prospect_service.initiate(
        db,
        user,
        campaign_id,
        prospect_id,
        background_tasks,
        lambda call_id: make_single_call(call_id, SessionLocal, eleven_labs_service),
    )


@router.get("/{campaign_id}/logs", response_model=List[CallOut])
def get_call_logs(
    campaign_id: int,
    status: Optional[CallStatus] = None,
    outcome: Optional[CallOutcome] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"get_call_logs called campaign_id={campaign_id} status={status} outcome={outcome} user={user.id}")
    return get_call_logs_service.list(db, user, campaign_id, status, outcome)


@router.get("/chat/{conversation_id}")
async def get_chat_by_conversation_id(
    conversation_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"get_chat_by_conversation_id called conversation_id={conversation_id} user={user.id}")
    return await get_chat_service.get(db, user, conversation_id, eleven_labs_service)

@router.get("/audio/{conversation_id}")
async def get_call_audio(
    conversation_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    logger.info(f"get_audio_by_conversion_id called conversation_id={conversation_id}")
    return await get_audio_service.get(db,user,conversation_id,eleven_labs_service)
    

@router.get("/{campaign_id}/stats")
def get_campaign_stats(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"get_campaign_stats called campaign_id={campaign_id} user={user.id}")
    return get_campaign_stats_service.stats(db, user, campaign_id)


@router.post("/{campaign_id}/refresh-outcomes", status_code=200)
def refresh_all_outcomes(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Re-run intent analysis on completed calls with transcripts but no outcome."""
    logger.info(f"refresh_all_outcomes called campaign_id={campaign_id} user={user.id}")
    return refresh_all_outcomes_service.refresh(
        db, user, campaign_id, eleven_labs_service
    )


@router.post("/{campaign_id}/calls/{call_id}/update-outcome")
def update_call_outcome(
    campaign_id: int,
    call_id: int,
    outcome: CallOutcome,
    interest_level: Optional[int] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"update_call_outcome called campaign_id={campaign_id} call_id={call_id} outcome={outcome}")
    return update_call_outcome_service.update(
        db, user, campaign_id, call_id, outcome, interest_level, notes
    )


@router.get("/{campaign_id}/hot-prospects")
def get_hot_prospects(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info(f"get_hot_prospects called campaign_id={campaign_id} user={user.id}")
    return get_hot_prospects_service.list(db, user, campaign_id)


@router.post("/webhook/conversation-complete")
async def conversation_webhook(
    payload: dict,
    db: Session = Depends(get_db),
):
    """ElevenLabs post-call webhook handler."""
    logger.info("conversation_webhook called")
    return conversation_webhook_service.handle(db, payload, eleven_labs_service)


@router.get("/voices")
async def list_voices():
    logger.info("list_voices called")
    return await list_voices_service.list(eleven_labs_service)
