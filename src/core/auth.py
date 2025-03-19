import logging

from fastapi import (
    Depends,
    HTTPException,
    Security,
    status,
)
from fastapi.security import APIKeyHeader

from src.core.settings import Settings, get_settings

logger = logging.getLogger(__name__)

API_KEY_HEADER = APIKeyHeader(name="X-API-Token", auto_error=False)


async def get_api_token(
    api_key_header: str = Security(API_KEY_HEADER),
    settings: Settings = Depends(get_settings),
) -> str:

    if api_key_header != settings.API_TOKEN:
        logger.warning("Invalid API token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API token",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key_header
