from datetime import datetime

import pytest

from src.controllers.schema import LockRequestSchema
from src.repos.state import StateRepository


@pytest.mark.asyncio
async def test_save_state(db_session):
    repo = StateRepository(db_session)

    state_hash = "test-hash"
    storage_path = "states/test-state/test-hash"
    operation_id = "test-op-id"

    result = await repo.save_state(state_hash, state_hash, storage_path, operation_id)

    assert result.name == state_hash
    assert result.state_hash == state_hash
    assert result.storage_path == storage_path
    assert result.operation_id == operation_id


@pytest.mark.asyncio
async def test_get_state_by_name(db_session):
    repo = StateRepository(db_session)

    state_name = "test-state"
    state_hash = "test-hash"
    storage_path = "states/test-state/test-hash"
    operation_id = "test-op-id"

    await repo.save_state(state_name, state_hash, storage_path, operation_id)

    state = await repo.get_by_name(state_name)
    assert state is not None
    assert state.name == state_name
    assert state.storage_path == storage_path
    assert state.operation_id == operation_id


@pytest.mark.asyncio
async def test_lock_unlock_state(db_session):
    repo = StateRepository(db_session)

    state_name = "lock-test-state"
    path = "test/path"

    await repo.save_state(state_name, "hash", path, "op-id")

    lock_data = LockRequestSchema(
        ID="test-lock-id",
        Path=path,
        Operation="test",
        Info="Test lock",
        Who="test-user",
        Version="1.0",
        created=datetime.now(),
    )

    lock_result = await repo.lock(state_name, lock_data)
    assert lock_result is True

    state = await repo.get_by_name(state_name)
    assert state.lock_id == lock_data.Id
    assert state.locked_by == lock_data.who
    assert state.locked_at is not None

    unlock_result = await repo.unlock(state_name, lock_data.Id)
    assert unlock_result is True

    state = await repo.get_by_name(state_name)
    assert state.lock_id is None
    assert state.locked_by is None
    assert state.locked_at is None


@pytest.mark.asyncio
async def test_create_state_on_lock(db_session):
    repo = StateRepository(db_session)
    state_name = "new-test-state"

    lock_data = LockRequestSchema(
        ID="new-state-lock-id",
        Path="test/path",
        Operation="test",
        Info="Test lock",
        Who="test-user",
        Version="1.0",
        created=datetime.now(),
    )

    lock_result = await repo.lock(state_name, lock_data)
    assert lock_result is True

    state = await repo.get_by_name(state_name)
    assert state is not None
    assert state.name == state_name
    assert state.lock_id == lock_data.Id
    assert state.locked_by == lock_data.who
