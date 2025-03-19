import logging
import platform
import sys
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, status

from src.controllers.schema import HealthResponse, InfoResponse
from src.core.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health() -> Dict[str, str]:
    return {"status": "healthy"}


@router.get("/info", response_model=InfoResponse, status_code=status.HTTP_200_OK)
async def info() -> Dict[str, Any]:
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "environment": settings.ENVIRONMENT.value,
        "timestamp": datetime.now().isoformat(),
        "system": {
            "python_version": sys.version,
            "platform": platform.platform(),
        },
    }
