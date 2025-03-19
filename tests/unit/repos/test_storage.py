from unittest.mock import AsyncMock, patch

import pytest

from src.repos.storage import MinioStorageRepository


@pytest.fixture
def mock_s3_client():
    mock_client = AsyncMock()

    mock_stream = AsyncMock()
    mock_stream.__aenter__.return_value = mock_stream
    mock_stream.read.return_value = b'{"version": 4, "terraform_version": "1.9.0"}'
    mock_client.get_object.return_value = {"Body": mock_stream}

    return mock_client


@pytest.fixture
def storage_repo(mock_s3_client):
    repo = MinioStorageRepository()
    with patch.object(
        repo,
        "_get_client",
        return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_s3_client),
            __aexit__=AsyncMock(),
        ),
    ):
        yield repo


@pytest.mark.asyncio
async def test_get(storage_repo, mock_s3_client):
    result = await storage_repo.get("test-path")

    assert result == b'{"version": 4, "terraform_version": "1.9.0"}'
    mock_s3_client.get_object.assert_called_once_with(
        Bucket=storage_repo.bucket_name, Key="test-path"
    )


@pytest.mark.asyncio
async def test_put(storage_repo, mock_s3_client):
    test_data = b'{"version": 4}'
    await storage_repo.put("test-path", test_data)

    mock_s3_client.put_object.assert_called_once_with(
        Bucket=storage_repo.bucket_name,
        Key="test-path",
        Body=test_data,
        ContentType="application/json",
    )


@pytest.mark.asyncio
async def test_ensure_bucket_exists(storage_repo, mock_s3_client):
    await storage_repo.ensure_bucket_exists()

    mock_s3_client.head_bucket.assert_called_once_with(Bucket=storage_repo.bucket_name)
