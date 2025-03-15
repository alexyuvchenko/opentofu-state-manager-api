import platform
import sys
from datetime import datetime
from typing import Any, Dict

from fastapi import (
    APIRouter,
    Request,
    status,
)
from fastapi.responses import JSONResponse

from src.controllers.schema import HealthResponse, InfoResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health() -> Dict[str, str]:
    """
    Health check endpoint.
    """
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "healthy"})


@router.get("/info", response_model=InfoResponse, status_code=status.HTTP_200_OK)
async def info(request: Request) -> Dict[str, Any]:
    """
    Information endpoint.
    """
    settings = request.app.state.settings
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT.value,
        "timestamp": datetime.now().isoformat(),
        "system": {
            "python_version": sys.version,
            "platform": platform.platform(),
        },
    }
