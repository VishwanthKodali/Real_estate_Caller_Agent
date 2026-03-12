from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.app.database.models import User
from .security import get_password_hash
from src.app.v1.models.auth_models import UserUpdate


class UserUpdateRequest:
    
    def update_user(db: Session,payload: UserUpdate, current_user: User):
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if payload.email and payload.email != user.email:
            if db.query(User).filter(User.email == payload.email).first():
                raise HTTPException(status_code=400, detail="Email already registered")
            user.email = payload.email
        if payload.password:
            user.hashed_password = get_password_hash(payload.password)
        db.commit()
        db.refresh(user)
        return user

update_user=UserUpdateRequest