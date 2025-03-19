from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class StateBaseSchema(BaseModel):
    name: str


class StateCreateSchema(StateBaseSchema):
    state_hash: str
    storage_path: str


class StateUpdateSchema(BaseModel):
    state_hash: Optional[str] = None
    storage_path: Optional[str] = None
    locked_by: Optional[str] = None
    locked_at: Optional[datetime] = None
    lock_id: Optional[str] = None
    operation_id: Optional[str] = None


class StateSchema(StateBaseSchema):
    id: int
    state_hash: str
    storage_path: str
    created_at: datetime
    updated_at: datetime
    locked_by: Optional[str] = None
    locked_at: Optional[datetime] = None
    lock_id: Optional[str] = None
    operation_id: Optional[str] = None

    class Config:
        from_attributes = True
