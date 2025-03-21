import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.controllers.schema import LockRequestSchema
from src.repos.state.schema import StateVersionSchema
from src.services.state import StateService


@pytest.fixture
def mock_state_repo():
    mock_repo = AsyncMock()
    mock_repo.get_by_name.return_value = None
    mock_repo.save_state.return_value = None
    mock_repo.lock.return_value = True
    mock_repo.unlock.return_value = True
    return mock_repo


@pytest.fixture
def mock_state_version_repo():
    mock_repo = AsyncMock()
    mock_repo.get_versions_by_state_id.return_value = []
    mock_repo.create_version.return_value = None
    return mock_repo


@pytest.fixture
def state_service(mock_state_repo, mock_state_version_repo, mock_storage_repository):
    """Create a state service with mock repositories for testing."""
    service = StateService(AsyncMock(), mock_storage_repository)
    service.state_repo = mock_state_repo
    service.state_version_repo = mock_state_version_repo
    return service


@pytest.mark.asyncio
async def test_get_state(
    state_service, mock_state_repo, mock_state_version_repo, mock_storage_repository
):
    test_data = json.dumps({"version": 4, "terraform_version": "1.9.0"})
    mock_storage_repository.storage["states/test-state/test-hash"] = test_data.encode()

    mock_state = MagicMock()
    mock_state.id = 1
    mock_state_repo.get_by_name.return_value = mock_state

    mock_version = StateVersionSchema(
        id=1,
        state_hash="test-hash",
        storage_path="states/test-state/test-hash",
        created_at=MagicMock(),
        operation_id="test-op",
        state_id=1,
    )
    mock_state_version_repo.get_versions_by_state_id.return_value = [mock_version]

    state_data = await state_service.get_state("test-state")

    assert json.loads(state_data) == {"version": 4, "terraform_version": "1.9.0"}


@pytest.mark.asyncio
async def test_save_state(
    state_service, mock_state_repo, mock_state_version_repo, mock_storage_repository
):
    mock_state = MagicMock()
    mock_state.id = 1
    mock_state_repo.save_state.return_value = mock_state

    state_data = json.dumps({"version": 4, "terraform_version": "1.9.0"}).encode()

    await state_service.save_state("test-state", state_data, "test-op-id")

    mock_state_version_repo.create_version.assert_called_once()


@pytest.mark.asyncio
async def test_lock_state(state_service):
    lock_data = LockRequestSchema(Id="test-lock-id", info="Test lock")

    result = await state_service.lock_state("test-state", lock_data)

    assert result is True


@pytest.mark.asyncio
async def test_unlock_state(state_service):
    result = await state_service.unlock_state("test-state", "test-lock-id")

    assert result is True
