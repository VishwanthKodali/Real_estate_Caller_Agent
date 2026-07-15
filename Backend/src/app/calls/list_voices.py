import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class ListVoicesRequest:

    async def list(elevenlabs_service):
        """List available ElevenLabs voices."""
        try:
            return await elevenlabs_service.list_voices()
        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            raise HTTPException(status_code=500, detail=str(e))


list_voices_service = ListVoicesRequest
