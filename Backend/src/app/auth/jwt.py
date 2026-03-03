import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.app.auth.token_blacklist import is_token_blacklisted
from src.app.common import get_logger, Settings

logger = get_logger("jwt")
security = HTTPBearer()

async def create_access_token(data: dict) -> str:
    """Create JWT access token with expiry"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=Settings.jwt_access_token_expire_minutes)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, Settings.jwt_secret_key, algorithm=Settings.jwt_algorithm)
    return encoded_jwt

async def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token with longer expiry"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=Settings.jwt_refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, Settings.jwt_secret_key, algorithm=Settings.jwt_algorithm)
    return encoded_jwt

async def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload if valid"""
    if await is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token revoked")
    try:
        payload = jwt.decode(token, Settings.jwt_secret_key, algorithms=[Settings.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current user from JWT token"""
    payload = await verify_token(credentials.credentials)
    
    # Ensure this is an access token, not a refresh token
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token: this is not an access token")
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    return {"username": username, "user_id": payload.get("user_id")}
