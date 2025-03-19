from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class StateBaseSchema(BaseModel):
    name: str


class StateUpdateSchema(BaseModel):
    locked_by: Optional[str] = None
    locked_at: Optional[datetime] = None
    lock_id: Optional[str] = None


class StateSchema(StateBaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime
    locked_by: Optional[str] = None
    locked_at: Optional[datetime] = None
    lock_id: Optional[str] = None

    class Config:
        from_attributes = True


class StateVersionCreateSchema(BaseModel):
    state_hash: str
    storage_path: str
    operation_id: str
    state_id: int


class StateVersionSchema(BaseModel):
    id: int
    state_hash: str
    storage_path: str
    created_at: datetime
    operation_id: str
    state_id: int

    class Config:
        from_attributes = True
