from datetime import datetime
from typing import (
    Dict,
    List,
    Optional,
)

from pydantic import BaseModel, Field


# Response models
class HealthResponse(BaseModel):
    status: str


class SystemInfo(BaseModel):
    python_version: str
    platform: str


class InfoResponse(BaseModel):
    app: str
    version: str
    environment: str
    timestamp: str
    system: SystemInfo


class LockRequestSchema(BaseModel):
    ID: str
    Info: Optional[str] = ""


class LockResponseSchema(BaseModel):
    status: str = "ok"
