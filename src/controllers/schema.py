from pydantic import BaseModel


# Response models
class HealthResponse(BaseModel):
    """Health check response model."""

    status: str


class SystemInfo(BaseModel):
    """System information model."""

    python_version: str
    platform: str


class InfoResponse(BaseModel):
    """Application information response model."""

    app: str
    version: str
    environment: str
    timestamp: str
    system: SystemInfo
