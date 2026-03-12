from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.app.database.models import User
from src.app.v1.models.auth_models import UserLogin
from .security import verify_password, create_access_token

class LoginRequest:

    def login(db: Session, payload: UserLogin):
        user = db.query(User).filter(User.email == payload.email).first()
        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token({"sub": str(user.id)})
        return {"access_token": token, "token_type": "bearer"}

login_user=LoginRequest