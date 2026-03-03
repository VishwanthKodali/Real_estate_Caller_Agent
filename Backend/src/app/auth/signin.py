import bcrypt
from sqlmodel import select
from src.app.database import User, PostgreSQLDB
from src.app.common import get_logger
from src.app.auth.jwt import create_access_token, create_refresh_token, verify_token

logger = get_logger("authentication")

def authenticate_user(username: str, password: str) -> dict:
    """Returns user dict if authenticated, raises exception otherwise"""
    try:
        with PostgreSQLDB.get_session() as session:
            statement = select(User).where(User.username == username)
            user = session.exec(statement).first()
            if not user:
                logger.warning(f"Authentication failed - user not found: {username}")
                raise ValueError("Invalid credentials")
            
            if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                logger.warning(f"Authentication failed - invalid password: {username}")
                raise ValueError("Invalid credentials")
            
            logger.debug(f"User authenticated successfully: {username}")
            return {
                "user_id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "company_name": user.company_name,
                "role": user.role
            }
    except Exception as e:
        logger.error(f"Error authenticating user {username}: {e}")
        raise ValueError("Authentication failed")

async def login_user(username: str, password: str):
    """Login and return tokens"""
    logger.debug(f"Authenticate function")
    user = authenticate_user(username, password)
    logger.debug(f"Creating tokens for user: {username}")
    access_token = await create_access_token({"sub": user["username"], "user_id": user["user_id"]})
    logger.debug(f"Access token created for user: {username}")
    refresh_token = await create_refresh_token({"sub": user["username"], "user_id": user["user_id"]})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }

async def refresh_access_token(refresh_token: str) -> dict:
    """Refresh access token using a valid refresh token"""
    payload = await verify_token(refresh_token)
    
    # Ensure this is a refresh token, not an access token
    if payload.get("type") != "refresh":
        raise ValueError("Invalid token: provided token is not a refresh token")
    
    new_access_token = await create_access_token({"sub": payload["sub"], "user_id": payload["user_id"]})
    return {"access_token": new_access_token, "token_type": "bearer"}
