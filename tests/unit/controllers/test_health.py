from unittest.mock import patch, MagicMock

import pytest
from fastapi import status

from src.controllers.schema import HealthResponse



@pytest.mark.asyncio
async def test_health_endpoint(async_client):

    response = await async_client.get("/health")
    
    assert response.status_code == status.HTTP_200_OK
    
    response_data = response.json()
    health_response = HealthResponse(**response_data)
    assert health_response.status == "healthy"


class MockDateTime:
    """Mock datetime class for testing with a fixed timestamp.
    
    This class mocks the datetime.now() method to return a MagicMock object
    that will return a fixed timestamp when isoformat() is called on it.
    """
    @staticmethod
    def now():
        """Return a mock datetime with a fixed timestamp."""
        mock_datetime = MagicMock()
        mock_datetime.isoformat.return_value = "2023-01-01T12:00:00"
        return mock_datetime


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
