import hashlib
import json
import logging
import uuid
from typing import (
    Dict,
    List,
    Optional,
    Type,
)

from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.schema import LockRequestSchema
from src.core.settings import StorageType, get_settings
from src.repos.state import StateRepository, StateVersionRepository
from src.repos.state.schema import StateVersionSchema
from src.repos.storage import BaseStorageRepository, MinioStorageRepository

logger = logging.getLogger(__name__)


INITIAL_STATE = {
    "version": 4,
    "terraform_version": "1.9.0",
    "serial": 0,
    "lineage": "",
    "outputs": {},
    "resources": [],
    "check_results": None,
}


def create_storage_repository() -> BaseStorageRepository:
    STORAGE_REPOSITORIES = {
        StorageType.MINIO: MinioStorageRepository,
        # StorageType.AWS_S3: AwsS3StorageRepository, # TODO: Add AWS S3 storage repository
    }

    settings = get_settings()
    repository_class = STORAGE_REPOSITORIES.get(settings.STORAGE_TYPE, StorageType.MINIO)

    if repository_class is None:
        raise ValueError(f"Unsupported storage type: {settings.STORAGE_TYPE}")

    return repository_class()


class StateService:
    def __init__(self, session: AsyncSession):
        self.state_repo = StateRepository(session)
        self.state_version_repo = StateVersionRepository(session)
        self.storage_repo: BaseStorageRepository = create_storage_repository()

    def _get_hash(self, state_data: bytes) -> str:
        return hashlib.sha256(state_data).hexdigest()

    def _generate_initial_state(self) -> bytes:
        initial_state = INITIAL_STATE.copy()
        initial_state["lineage"] = str(uuid.uuid4())
        return json.dumps(initial_state).encode()

    async def get_state(self, name: str) -> bytes:
        state = await self.state_repo.get_by_name(name)

        if not state:
            logger.info(f"No state found for {name}, returning initial state")
            return self._generate_initial_state()

        versions = await self.state_version_repo.get_versions_by_state_id(state.id)
        if not versions:
            logger.info(f"No state versions found for {name}, returning initial state")
            return self._generate_initial_state()

        latest_version = versions[0]
        state_data = await self.storage_repo.get(latest_version.storage_path)

        if not state_data:
            logger.warning(
                f"State file not found in storage at {latest_version.storage_path}, returning initial state"
            )
            return self._generate_initial_state()

        return state_data

    async def save_state(self, name: str, state_data: bytes, operation_id: str) -> None:
        await self.storage_repo.ensure_bucket_exists()

        try:
            json.loads(state_data)
        except json.JSONDecodeError as exc:
            logger.error(f"Invalid JSON in state data: {exc}")
            raise ValueError(f"Invalid JSON in state data: {str(exc)}")

        state_hash = self._get_hash(state_data)
        storage_path = f"states/{name}/{state_hash}_{operation_id}"

        logger.info(f"Saving state for {name}, hash: {state_hash}, operation: {operation_id}")
        await self.storage_repo.put(storage_path, state_data)

        state = await self.state_repo.save_state(name)
        if state and state.id:
            await self.state_version_repo.create_version(
                state_hash=state_hash,
                storage_path=storage_path,
                operation_id=operation_id,
                state_id=state.id,
            )

    async def lock_state(self, name: str, lock_data: LockRequestSchema) -> bool:
        return await self.state_repo.lock(name, lock_data)

    async def unlock_state(self, name: str, lock_id: str) -> bool:
        return await self.state_repo.unlock(name, lock_id)

    async def get_state_versions(self, name: str) -> List[StateVersionSchema]:
        state = await self.state_repo.get_by_name(name)
        if not state:
            return []
        return await self.state_version_repo.get_versions_by_state_id(state.id)

    async def get_state_version(self, name: str, version_id: int) -> Optional[StateVersionSchema]:
        state = await self.state_repo.get_by_name(name)
        if not state:
            return None

        version = await self.state_version_repo.get_version_by_id(state.id, version_id)
        if not version:
            return None

        return version
