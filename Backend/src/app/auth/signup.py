import bcrypt
from sqlmodel import select
import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Optional
from src.app.database import PostgreSQLDB, User
from src.app.common import get_logger

logger = get_logger("registration")

class RegistrationResult(Enum):
    SUCCESS = "success"
    ALREADY_EXISTS = "already_exists"
    VALIDATION_ERROR = "validation_error"

@dataclass
class RegistrationResponse:
    success: bool
    result: RegistrationResult
    message: Optional[str] = None
    user_id: Optional[int] = None

def generate_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def register_user(full_name: str, company_name: str, username: str, password: str, 
                 contact_number: str, email: str, office_address: str, 
                 website: str = "", rera_number: str = "") -> RegistrationResponse:
    try:
        with PostgreSQLDB.get_session() as session:
            # Validate required fields
            if not all([full_name, company_name, username, password, email, contact_number]):
                return RegistrationResponse(
                    success=False, 
                    result=RegistrationResult.VALIDATION_ERROR,
                    message="All required fields must be provided"
                )
            
            # Check if user already exists
            statement = select(User).where(User.username == username)
            existing_user = session.exec(statement).first()
            if existing_user:
                logger.warning(f"User already exists: {username}")
                return RegistrationResponse(
                    success=False, 
                    result=RegistrationResult.ALREADY_EXISTS,
                    message="Username already registered"
                )
            
            # Hash password
            hashed_password = generate_password_hash(password)
            created_at = datetime.datetime.utcnow()
            
            # Create new user
            user = User(
                full_name=full_name,
                company_name=company_name,
                username=username,
                password=hashed_password,
                role="admin",
                contact_number=contact_number,
                email=email,
                office_address=office_address,
                website=website,
                rera_number=rera_number,
                created_at=created_at
            )
            
            session.add(user)
            session.commit()
            session.refresh(user)
            
            logger.debug(f"User registered successfully: {username}")
            return RegistrationResponse(
                success=True,
                result=RegistrationResult.SUCCESS,
                message="User registered successfully",
                user_id=user.id
            )
    except Exception as e:
        logger.exception(f"Error registering user {username}: {e}")
        return RegistrationResponse(
            success=False,
            result=RegistrationResult.VALIDATION_ERROR,
            message="Registration failed. Please try again."
        )
