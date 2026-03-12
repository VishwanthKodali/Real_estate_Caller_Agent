from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.app.database.models import User
from src.app.v1.models.auth_models import UserRegister
from .security import get_password_hash

class _RegisterRequest:

    def register(db: Session, payload: UserRegister):
        if db.query(User).filter(User.email == payload.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        user = User(
            email=payload.email,
            hashed_password=get_password_hash(payload.password),
            full_name=payload.full_name,
            company_name=payload.company_name,
            phone=payload.phone
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

register_user=_RegisterRequest