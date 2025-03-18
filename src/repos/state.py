"""
State repository for database operations.
"""

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import State

logger = logging.getLogger(__name__)


class StateRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, name: str) -> Optional[State]:
        query = select(State).where(State.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def lock(self, name: str, lock_id: str, info: str) -> bool:
        state = await self.get_by_name(name)

        if not state:
            state = State(
                name=name,
                state_hash="",
                storage_path=f"states/{name}/initial",
                locked_by=info,
                locked_at=datetime.now(),
                lock_id=lock_id,
            )
            self.session.add(state)
            await self.session.commit()
            return True

        if state.locked_by:
            return False

        state.locked_by = info
        state.locked_at = datetime.now()
        state.lock_id = lock_id
        await self.session.commit()
        return True

    async def unlock(self, name: str, lock_id: str) -> bool:
        state = await self.get_by_name(name)

        if not state or state.lock_id != lock_id:
            return False

        state.locked_by = None
        state.locked_at = None
        state.lock_id = None
        await self.session.commit()
        return True

    async def save_state(self, name: str, state_hash: str, storage_path: str) -> State:
        state = await self.get_by_name(name)

        if state:
            state.state_hash = state_hash
            state.storage_path = storage_path
            state.updated_at = datetime.now()
        else:
            state = State(name=name, state_hash=state_hash, storage_path=storage_path)
            self.session.add(state)

        await self.session.commit()
        await self.session.refresh(state)
        return state
