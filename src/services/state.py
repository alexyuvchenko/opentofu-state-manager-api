import hashlib
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.repos.state import StateRepository
from src.repos.storage import BaseStorageRepository, MinioStorageRepository

logger = logging.getLogger(__name__)


EMPTY_STATE = {
    "version": 3,
    "terraform_version": "1.1.0",
    "serial": 1,
    "lineage": "",
    "outputs": {},
    "resources": [],
}


class StateService:
    def __init__(self, session: AsyncSession):
        self.state_repo = StateRepository(session)
        self.storage_repo: BaseStorageRepository = MinioStorageRepository()

    def _get_hash(self, state_data: bytes) -> str:
        return hashlib.sha256(state_data).hexdigest()

    def _ensure_valid_state_format(self, state_data: bytes) -> bytes:
        """Ensure state data is in the correct format for OpenTofu."""
        try:
            # Convert bytes to string if needed
            state_str = state_data.decode("utf-8") if isinstance(state_data, bytes) else state_data

            # Parse JSON data
            if isinstance(state_str, str):
                json_data = json.loads(state_str)
            else:
                json_data = state_str

            # Ensure version is an integer
            if not isinstance(json_data.get("version"), int):
                json_data["version"] = 4

            return json.dumps(json_data).encode()
        except json.JSONDecodeError:
            return json.dumps(EMPTY_STATE).encode()

    async def get_state(self, name: str) -> bytes:
        """Get the OpenTofu state."""
        state = await self.state_repo.get_by_name(name)

        if not state:
            logger.info(f"No state found for {name}, returning empty state")
            return None

        state_data = await self.storage_repo.get(state.storage_path)

        if not state_data:
            logger.warning(
                f"State file not found in storage at {state.storage_path}, returning empty state"
            )
            return None

        return self._ensure_valid_state_format(state_data)

    async def save_state(self, name: str, state_data: bytes) -> None:
        await self.storage_repo.ensure_bucket_exists()

        try:
            json.loads(state_data)
            formatted_state = self._ensure_valid_state_format(state_data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in state data: {e}")
            raise ValueError(f"Invalid JSON in state data: {str(e)}")

        state_hash = self._get_hash(formatted_state)
        logger.info(f"Saving state for {name}, hash: {state_hash}")

        storage_path = f"states/{name}/{state_hash}"
        await self.storage_repo.put(storage_path, formatted_state)
        await self.state_repo.save_state(name, state_hash, storage_path)

    async def lock_state(self, name: str, lock_id: str, info: str) -> bool:
        return await self.state_repo.lock(name, lock_id, info)

    async def unlock_state(self, name: str, lock_id: str) -> bool:
        return await self.state_repo.unlock(name, lock_id)
