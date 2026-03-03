from fastapi import APIRouter,HTTPException, Depends
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from src.app.auth import login_user, register_user, refresh_access_token, blacklist_current_token
from src.app.v1.models.auth_models import UserLogin, UserRegistration, TokenRefresh, LogoutRequest
from src.app.common import get_logger

logger = get_logger("auth_router")
router = APIRouter(prefix="/v1/auth", tags=["Authentication"])
security = HTTPBearer()

@router.post(
    "/register",
    response_model=dict,
    status_code=200,
    summary="Register new user",
    description="Register a new real estate developer with company details.",
    responses={
        200: {"description": "User registered successfully"},
        400: {"description": "Validation error or user already exists"}
    }
)
async def register(registration: UserRegistration):
    """
    Register a new user account.
    
    **Required Fields:**
    - full_name: Developer's full name
    - company_name: Real estate company name
    - username: Unique username
    - password: Min 8 chars, must contain uppercase, lowercase, number
    - email: Company email
    - contact_number: Phone number
    - office_address: Company office address
    
    **Optional Fields:**
    - website: Company website URL
    - rera_number: RERA registration number
    """
    try:
        result = register_user(
            registration.full_name, 
            registration.company_name, 
            registration.username,
            registration.password, 
            registration.contact_number, 
            registration.email,
            registration.office_address, 
            registration.website, 
            registration.rera_number
        )
        if not result.success:
            logger.warning(f"Registration failed: {result.message}")
            raise HTTPException(status_code=400, detail=result.message)
        logger.info(f"User registered successfully: {registration.username}")
        return {
            "message": result.message, 
            "user_id": result.user_id,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post(
    "/login",
    response_model=dict,
    summary="User login",
    description="Authenticate user and get access/refresh tokens.",
    responses={
        200: {"description": "Login successful, tokens returned"},
        401: {"description": "Invalid credentials"}
    }
)
async def login(auth: UserLogin):
    """
    Login with username and password.
    Returns JWT access token and refresh token.
    """
    try:
        tokens = await login_user(auth.username, auth.password)
        logger.info(f"User logged in: {auth.username}")
        return tokens
    except ValueError as e:
        logger.warning(f"Login failed for {auth.username}: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.post(
    "/refresh",
    response_model=dict,
    summary="Refresh access token",
    description="Get a new access token using refresh token.",
    responses={
        200: {"description": "New access token generated"},
        401: {"description": "Invalid or expired refresh token"}
    }
)
async def refresh_token(token: TokenRefresh):
    """
    Refresh the access token using a valid refresh token.
    """
    try:
        new_tokens = await refresh_access_token(token.refresh_token)
        logger.info("Access token refreshed")
        return new_tokens
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post(
    "/logout",
    response_model=dict,
    summary="Logout user",
    description="Revoke current access token (and optionally refresh token).",
    responses={
        200: {"description": "Logout successful"},
        401: {"description": "Invalid token"}
    }
)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security), logout_req: LogoutRequest = None):
    """
    Logout and blacklist the current access token (and optionally refresh token).
    Tokens will no longer be valid for API requests.
    
    **Header:**
    - Authorization: Bearer <access_token>
    
    **Body (optional):**
    - refresh_token: The refresh token to revoke as well.
    """
    try:
        access_token = credentials.credentials
        refresh_token = logout_req.refresh_token if logout_req else None
        result = await blacklist_current_token(access_token, refresh_token)
        logger.info("User logged out successfully")
        return result
    except HTTPException:
        raise  # Re-raise HTTP exceptions from blacklist_current_token
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(status_code=401, detail="Logout failed")


