import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.schema import LockRequestSchema
from src.db.models import State, StateVersion
from src.repos.schema import (
    StateSchema,
    StateUpdateSchema,
    StateVersionCreateSchema,
    StateVersionSchema,
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
            state = State(
                name=name,
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

    async def unlock(self, name: str, lock_id: str) -> Optional[bool]:
        state = await self.get_by_name(name)

        if not state:
            return None

        if state.lock_id != lock_id:
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

    async def save_state(self, name: str) -> StateSchema:
        state = await self.get_by_name(name)

        if state:
            state.updated_at = datetime.now()
        else:
            state = State(name=name)
            self.session.add(state)

        await self.session.commit()
        await self.session.refresh(state)

        return StateSchema.model_validate(state)


class StateVersionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_version(
        self, state_hash: str, storage_path: str, operation_id: str, state_id: int
    ) -> StateVersionSchema:
        state_version_data = StateVersionCreateSchema(
            state_hash=state_hash,
            storage_path=storage_path,
            operation_id=operation_id,
            state_id=state_id,
        )

        state_version = StateVersion(
            state_hash=state_version_data.state_hash,
            storage_path=state_version_data.storage_path,
            operation_id=state_version_data.operation_id,
            state_id=state_version_data.state_id,
        )

        self.session.add(state_version)
        await self.session.commit()
        await self.session.refresh(state_version)

        return StateVersionSchema.model_validate(state_version)

    async def get_versions_by_state_id(self, state_id: int) -> List[StateVersionSchema]:
        query = (
            select(StateVersion)
            .where(StateVersion.state_id == state_id)
            .order_by(StateVersion.created_at.desc())
        )
        result = await self.session.execute(query)
        versions = result.scalars().all()

        return [StateVersionSchema.model_validate(version) for version in versions]

    async def get_version_by_id(
        self, state_id: int, version_id: int
    ) -> Optional[StateVersionSchema]:
        query = select(StateVersion).where(
            StateVersion.state_id == state_id, StateVersion.id == version_id
        )
        result = await self.session.execute(query)
        state_version = result.scalars().first()

        if not state_version:
            return None

        return StateVersionSchema.model_validate(state_version)
