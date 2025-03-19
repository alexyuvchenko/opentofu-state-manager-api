import json
from datetime import datetime

import pytest
from fastapi import status

from src.controllers.schema import LockRequestSchema
from src.services.state import StateService

STATE_DATA = {"version": 4, "terraform_version": "1.9.0", "lineage": "test-lineage"}


@pytest.mark.asyncio
async def test_get_state(db_session, auth_async_client):
    service = StateService(db_session)
    await service.save_state(
        "state_identifier", json.dumps(STATE_DATA).encode(), "test-operation-id"
    )

    response = await auth_async_client.get("/state_identifier")
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert "version" in response_data
    assert "terraform_version" in response_data
    assert "lineage" in response_data
    assert response_data["version"] == 4


@pytest.mark.asyncio
async def test_save_state(db_session, auth_async_client):
    state_data = json.dumps(STATE_DATA)

    response = await auth_async_client.post(
        "/state_identifier?ID=test-operation-id",
        content=state_data,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_lock_state(db_session, auth_async_client):
    lock_data = {
        "ID": "test-lock-id",
        "Path": "test/path",
        "Operation": "test",
        "Info": "Test lock",
        "Who": "test-user",
        "Version": "1.0",
        "Created": datetime.now().isoformat(),
    }

    response = await auth_async_client.request(
        "LOCK",
        "/state_identifier/lock",
        json=lock_data,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_unlock_state(db_session, auth_async_client):

    lock_data = {
        "ID": "test-lock-id",
        "Path": "test/path",
        "Operation": "test",
        "Info": "Test lock",
        "Who": "test-user",
        "Version": "1.0",
        "Created": datetime.now().isoformat(),
    }

    service = StateService(db_session)
    lock = LockRequestSchema(**lock_data)

    await service.lock_state("state_identifier", lock)

    response = await auth_async_client.request(
        "UNLOCK",
        "/state_identifier/unlock",
        json={"ID": "test-lock-id"},
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_get_state_version(db_session, auth_async_client):
    service = StateService(db_session)
    await service.save_state(
        "state_identifier", json.dumps(STATE_DATA).encode(), "test-operation-id"
    )

    response = await auth_async_client.get("/state_identifier/versions/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["operation_id"] == "test-operation-id"


@pytest.mark.asyncio
async def test_get_state_version_not_found(db_session, auth_async_client):
    response = await auth_async_client.get("/state_identifier/versions/999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"]
