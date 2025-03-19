from datetime import datetime

from pydantic import BaseModel, Field


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
    Id: str = Field(default="", alias="ID")
    info: str = Field(default="", alias="Info")
    created: datetime = Field(default_factory=datetime.now, alias="Created")
    operation: str = Field(default="", alias="Operation")
    path: str = Field(default="", alias="Path")
    version: str = Field(default="", alias="Version")
    who: str = Field(default="", alias="Who")


class LockResponseSchema(BaseModel):
    status: str = "ok"


class StateVersionResponseSchema(BaseModel):
    id: int
    state_hash: str
    storage_path: str
    created_at: datetime
    operation_id: str
    state_id: int


class StateVersionListResponseSchema(BaseModel):
    data: list[StateVersionResponseSchema]
