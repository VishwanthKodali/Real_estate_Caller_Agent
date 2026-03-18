import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.app.database.db import get_db
from src.app.auth.security import get_current_user
from src.app.dashboard import GetDashboardStatsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db), user=Depends(get_current_user)):
    logger.info(f"get_dashboard_stats called user={getattr(user,'id',None)}")
    return GetDashboardStatsService.get_stats(db, user)
