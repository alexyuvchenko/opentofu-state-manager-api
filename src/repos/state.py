import logging
from datetime import datetime, tzinfo
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.schema import LockRequestSchema
from src.db.models import State
from src.repos.schema import (
    StateCreateSchema,
    StateSchema,
    StateUpdateSchema,
)

logger = logging.getLogger(__name__)


class StateRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, name: str) -> Optional[State]:
        query = select(State).where(State.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def lock(self, name: str, lock_data: LockRequestSchema) -> bool:
        state = await self.get_by_name(name)

        if not state:
            state_data = StateCreateSchema(
                name=name,
                state_hash="",
                storage_path=f"states/{name}/initial",
            )
            state = State(
                name=state_data.name,
                state_hash=state_data.state_hash,
                storage_path=state_data.storage_path,
                locked_by=lock_data.who,
                locked_at=lock_data.created.replace(tzinfo=None),
                lock_id=lock_data.Id,
            )
            self.session.add(state)
            await self.session.commit()
            return True

        if state.locked_by:
            return False

        # Lock the state
        update_data = StateUpdateSchema(
            locked_by=lock_data.who,
            locked_at=lock_data.created.replace(tzinfo=None),
            lock_id=lock_data.Id,
        )
        state.locked_by = update_data.locked_by
        state.locked_at = update_data.locked_at
        state.lock_id = update_data.lock_id
        await self.session.commit()
        return True

    async def unlock(self, name: str, lock_id: str) -> bool:
        state = await self.get_by_name(name)

        if not state or state.lock_id != lock_id:
            return False

        update_data = StateUpdateSchema(
            locked_by=None,
            locked_at=None,
            lock_id=None,
        )
        state.locked_by = update_data.locked_by
        state.locked_at = update_data.locked_at
        state.lock_id = update_data.lock_id
        await self.session.commit()
        return True

    async def save_state(
        self, name: str, state_hash: str, storage_path: str, operation_id: str
    ) -> StateSchema:
        state = await self.get_by_name(name)

        if state:
            update_data = StateUpdateSchema(
                state_hash=state_hash,
                storage_path=storage_path,
            )
            state.state_hash = update_data.state_hash
            state.storage_path = update_data.storage_path
            state.updated_at = datetime.now()
            state.operation_id = operation_id
        else:
            state_data = StateCreateSchema(
                name=name,
                state_hash=state_hash,
                storage_path=storage_path,
            )
            state = State(
                name=state_data.name,
                state_hash=state_data.state_hash,
                storage_path=state_data.storage_path,
                operation_id=operation_id,
            )
            self.session.add(state)

        await self.session.commit()
        await self.session.refresh(state)
        return StateSchema.model_validate(state)
