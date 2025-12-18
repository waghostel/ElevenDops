"""Property tests for BackendAPIClient audio methods."""

from unittest.mock import MagicMock, patch, AsyncMock

import pytest
from hypothesis import given
from hypothesis import strategies as st

from streamlit_app.services.backend_api import BackendAPIClient


@pytest.mark.asyncio
@given(
    st.text(min_size=1),
    st.text(min_size=1),
    st.text(min_size=1),
)
async def test_audio_generation_request_preserves_script(knowledge_id: str, script: str, voice_id: str):
    """**Feature: education-audio-page, Property 6: Script Edit Preservation**
    
    Validates that the generate_audio method preserves the (potentially edited) script
    content when sending the request to the backend.
    """
    client = BackendAPIClient()
    
    # Mock httpx response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "audio_id": "test_id",
        "audio_url": "http://test.url",
        "knowledge_id": knowledge_id,
        "voice_id": voice_id,
        "script": script,  # Backend echoes back script
        "created_at": "2023-10-27T10:00:00"
    }
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        
        await client.generate_audio(knowledge_id=knowledge_id, script=script, voice_id=voice_id)
        
        # Verify request payload
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args.kwargs
        payload = call_kwargs["json"]
        
        assert payload["script"] == script
        assert payload["knowledge_id"] == knowledge_id
        assert payload["voice_id"] == voice_id
