import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.app.database import get_db
from src.app.database.models import User
from src.app.v1.models.auth_models import UserRegister, UserLogin, Token, UserOut, UserUpdate
from src.app.auth import login_user, register_user, update_user, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    logger.info("auth.register called")
    return register_user.register(db, payload)
    


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    logger.info("auth.login called")
    return login_user.login(db, payload)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    logger.info(f"auth.get_me called user={current_user.id}")
    return current_user


@router.put("/me", response_model=UserOut)
def update_me(payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.info(f"auth.update_me called user={current_user.id}")
    return update_user.update_user(db, payload, current_user)
