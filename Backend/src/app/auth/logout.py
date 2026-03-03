import jwt
import time
from fastapi import HTTPException
from src.app.auth.token_blacklist import add_to_blacklist
from src.app.common import get_logger, Settings
from src.app.auth.jwt import verify_token

logger = get_logger("logout")

async def blacklist_current_token(access_token: str, refresh_token: str = None) -> dict:
    """
    Verify tokens (access and optional refresh) to identify the user, then
    blacklist them until their expiry. Returns success message.
    - Verifies signature & expiry via `verify_token()` so we know which user
      the tokens belong to (`sub` claim).
    - Ensures token-type expectations (access vs refresh) before blacklisting.
    """
    try:
        # Verify access token (will raise HTTPException on invalid/expired/blacklisted)
        apayload = await verify_token(access_token)
        if apayload.get("type") != "access":
            raise HTTPException(status_code=400, detail="Provided token is not an access token")

        expiry_timestamp = apayload.get("exp", time.time() + 3600)
        add_to_blacklist(access_token, expiry_timestamp)
        logger.info(f"Access token blacklisted for user: {apayload.get('sub', 'unknown')}")

        # If a refresh token was provided, verify it and blacklist too
        if refresh_token:
            try:
                rpayload = await verify_token(refresh_token)
                if rpayload.get("type") != "refresh":
                    raise HTTPException(status_code=400, detail="Provided token is not a refresh token")
                rexp = rpayload.get("exp", time.time() + 24 * 3600)
                await add_to_blacklist(refresh_token, rexp)
                logger.info(f"Refresh token blacklisted for user: {rpayload.get('sub', 'unknown')}")
            except HTTPException as e:
                # If refresh token is invalid/expired/blacklisted, log and skip
                logger.warning(f"Refresh token not blacklisted: {e.detail}")

        return {"message": "Logged out successfully - token(s) revoked"}

    except HTTPException:
        # Re-raise HTTPExceptions from verify_token so callers get proper HTTP response
        raise
    except Exception as e:
        logger.error(f"Unexpected error during logout: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid token format")
