import redis.asyncio as redis
import time
from src.app.common import get_logger, Settings

logger = get_logger("token_blacklist")
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

async def add_to_blacklist(token: str, expiry_timestamp: int):
    ttl = int(expiry_timestamp - time.time())
    if ttl > 0:
        await redis_client.setex(f"{Settings.jwt_blacklist_key}:{token}", ttl, "1")
        logger.debug(f"Token blacklisted with TTL {ttl}s: {token[:20]}...")

async def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted asynchronously"""
    exists = await redis_client.exists(f"{Settings.jwt_blacklist_key}:{token}")
    return bool(exists)


async def cleanup_expired_tokens():
    """Cleanup expired tokens asynchronously (run periodically)"""
    keys = await redis_client.keys(f"{Settings.jwt_blacklist_key}:*")
    for key in keys:
        # Extend expiry if still active
        await redis_client.expire(key, 3600)
        logger.debug(f"Extended TTL for token key: {key}")