
import pytest
from unittest.mock import AsyncMock, patch
import httpx
from streamlit_app.services.backend_api import BackendAPIClient, APIError, APIConnectionError

# **Feature: error-handling, Property 8: Error Logging Without UI Exposure**
# **Validates: Requirements 7.4**

@pytest.mark.asyncio
async def test_property_8_error_logging_without_ui_exposure():
    """
    Property 8: Error Logging Without UI Exposure
    The system must catch backend errors and raise structured APIError exceptions,
    ensuring that raw stack traces are not exposed.
    """
    client = BackendAPIClient()

    # Simulate connection error
    with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Connection refused")):
        with pytest.raises(APIConnectionError) as excinfo:
            await client.create_patient_session("p1", "a1")
        assert "Failed to connect to backend" in str(excinfo.value)
        # Ensure it's not a raw exception leaking

    # Simulate HTTP error (e.g. 500)
    mock_request = httpx.Request("POST", "http://test")
    mock_response = httpx.Response(500, text="Internal Server Error", request=mock_request)
    # need to patch context manager or internal client method
    
    with patch.object(BackendAPIClient, '_get_client') as mock_get_client:
        mock_client_instance = AsyncMock()
        mock_get_client.return_value = mock_client_instance
        # Async context manager mock
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        
        mock_client_instance.post.return_value = mock_response
        
        with pytest.raises(APIError) as excinfo:
            await client.create_patient_session("p1", "a1")
        
        assert excinfo.value.status_code == 500
        assert "Failed to create session" in str(excinfo.value)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_property_8_error_logging_without_ui_exposure())
