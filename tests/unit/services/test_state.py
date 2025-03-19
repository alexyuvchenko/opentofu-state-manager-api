import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.controllers.schema import LockRequestSchema
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
def mock_storage_repo():
    mock_repo = AsyncMock()
    mock_repo.get.return_value = json.dumps({"version": 4, "terraform_version": "1.9.0"}).encode()
    mock_repo.put.return_value = None
    mock_repo.ensure_bucket_exists.return_value = None
    return mock_repo


@pytest.fixture
def state_service(mock_state_repo, mock_storage_repo):
    service = StateService(AsyncMock())
    service.state_repo = mock_state_repo
    service.storage_repo = mock_storage_repo
    return service


@pytest.mark.asyncio
async def test_get_state(state_service, mock_state_repo, mock_storage_repo):
    mock_state = MagicMock()
    mock_state.storage_path = "states/test-state/test-hash"
    mock_state_repo.get_by_name.return_value = mock_state

    state_data = await state_service.get_state("test-state")

    assert json.loads(state_data) == {"version": 4, "terraform_version": "1.9.0"}


@pytest.mark.asyncio
async def test_save_state(state_service, mock_state_repo, mock_storage_repo):
    state_data = json.dumps({"version": 4, "terraform_version": "1.9.0"}).encode()

    await state_service.save_state("test-state", state_data, "test-op-id")


@pytest.mark.asyncio
async def test_lock_state(state_service, mock_state_repo):
    lock_data = LockRequestSchema(Id="test-lock-id", info="Test lock")

    result = await state_service.lock_state("test-state", lock_data)

    assert result is True


@pytest.mark.asyncio
async def test_unlock_state(state_service, mock_state_repo):
    result = await state_service.unlock_state("test-state", "test-lock-id")

    assert result is True
