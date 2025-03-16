import hashlib
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import State
from src.services.storage import MinIOStorageBackend, StorageBackend


class StateService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.storage: StorageBackend = MinIOStorageBackend()

    def _calculate_hash(self, state_data: bytes) -> str:
        return hashlib.sha256(state_data).hexdigest()

    async def get_state(self, name: str) -> Optional[bytes]:
        query = select(State).where(State.name == name)
        result = await self.session.execute(query)
        state = result.scalar_one_or_none()

        if not state:
            return None

        return await self.storage.get(state.storage_path)

    async def save_state(self, name: str, state_data: bytes) -> None:
        state_hash = self._calculate_hash(state_data)
        storage_path = f"states/{name}/{state_hash}.tfstate"

        # Save to storage
        await self.storage.put(storage_path, state_data)

        # Update database
        query = select(State).where(State.name == name)
        result = await self.session.execute(query)
        state = result.scalar_one_or_none()

        if state:
            state.state_hash = state_hash
            state.storage_path = storage_path
            state.updated_at = datetime.utcnow()
        else:
            state = State(name=name, state_hash=state_hash, storage_path=storage_path)
            self.session.add(state)

        await self.session.commit()

    async def lock_state(self, name: str, lock_id: str, info: str) -> bool:
        query = select(State).where(State.name == name)
        result = await self.session.execute(query)
        state = result.scalar_one_or_none()

        if not state:
            return False

        if state.locked_by:
            return False

        state.locked_by = info
        state.locked_at = datetime.now()
        state.lock_id = lock_id
        await self.session.commit()
        return True

    async def unlock_state(self, name: str, lock_id: str) -> bool:
        query = select(State).where(State.name == name)
        result = await self.session.execute(query)
        state = result.scalar_one_or_none()

        if not state or state.lock_id != lock_id:
            return False

        state.locked_by = None
        state.locked_at = None
        state.lock_id = None
        await self.session.commit()
        return True
