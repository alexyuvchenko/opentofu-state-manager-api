from unittest.mock import MagicMock, patch

import pytest
from fastapi import status

from src.controllers.schema import HealthResponse


@pytest.mark.asyncio
async def test_health_endpoint(async_client):

    response = await async_client.get("/health")

    assert response.status_code == status.HTTP_200_OK

    health_response = HealthResponse(**response.json())

    assert health_response.status == "healthy"


@pytest.mark.asyncio
async def test_info_endpoint(async_client):

    mock_settings = MagicMock()

    mock_settings.APP_NAME = "Test App"
    mock_settings.APP_VERSION = "1.0.0"
    mock_settings.APP_DESCRIPTION = "Test Description"
    mock_settings.ENVIRONMENT.value = "local"

    with patch("src.controllers.health.settings", mock_settings):

        response = await async_client.get("/info")

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()

        assert response_data["app_name"] == "Test App"
