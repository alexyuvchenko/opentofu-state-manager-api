import json
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

from src.repos.schema import StateVersionSchema

STATE_DATA = {"version": 4, "terraform_version": "1.9.0", "lineage": "test-lineage"}


@pytest.fixture
def mock_state_service():
    mock_service = AsyncMock()

    mock_service.get_state.return_value = json.dumps(STATE_DATA).encode()
    mock_service.save_state.return_value = None
    mock_service.lock_state.return_value = True
    mock_service.unlock_state.return_value = True

    return mock_service


@pytest.mark.asyncio
async def test_get_state(async_client, mock_state_service):
    with patch("src.controllers.opentofu.get_state_service", return_value=mock_state_service):
        response = await async_client.get("/state_identifier")
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert "version" in response_data
        assert "terraform_version" in response_data
        assert "lineage" in response_data
        assert response_data["version"] == 4


@pytest.mark.asyncio
async def test_save_state(async_client, mock_state_service):
    state_data = json.dumps(STATE_DATA)

    with patch("src.controllers.opentofu.get_state_service", return_value=mock_state_service):
        response = await async_client.post(
            "/state_identifier?ID=test-operation-id",
            content=state_data,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_lock_state(async_client, mock_state_service):
    lock_data = {
        "ID": "test-lock-id",
        "Info": "Test lock",
        "Operation": "plan",
        "Path": "test-path",
        "Version": "1.0",
        "Who": "test-user",
    }

    with patch("src.controllers.opentofu.get_state_service", return_value=mock_state_service):
        response = await async_client.request(
            "LOCK",
            "/state_identifier/lock",
            json=lock_data,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_unlock_state(async_client, mock_state_service):
    unlock_data = {
        "ID": "test-lock-id",
        "Info": "Test unlock",
        "Operation": "plan",
        "Path": "test-path",
        "Version": "1.0",
        "Who": "test-user",
    }

    with patch("src.controllers.opentofu.get_state_service", return_value=mock_state_service):
        response = await async_client.request(
            "UNLOCK",
            "/state_identifier/unlock",
            json=unlock_data,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_get_state_version(async_client, mock_state_service):
    version = StateVersionSchema(
        id=1,
        state_hash="hash1",
        storage_path="states/state_identifier/test-operation-id",
        created_at=datetime.now(),
        operation_id="test-operation-id",
        state_id=1,
    )

    # Directly patch the method in the StateService class
    with patch("src.services.state.StateService.get_state_version", return_value=version):
        response = await async_client.get("/state_identifier/versions/1")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert response_data["id"] == 1
        assert response_data["operation_id"] == "test-operation-id"


@pytest.mark.asyncio
async def test_get_state_version_not_found(async_client, mock_state_service):
    with patch("src.services.state.StateService.get_state_version", return_value=None):
        response = await async_client.get("/state_identifier/versions/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]
