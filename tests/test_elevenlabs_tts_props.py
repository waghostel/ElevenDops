"""Property tests for ElevenLabs service TTS functionality."""

from unittest.mock import MagicMock, patch

from hypothesis import given
from hypothesis import strategies as st

from backend.services.elevenlabs_service import ElevenLabsService, get_elevenlabs_service


@given(
    st.text(min_size=1),
    st.text(min_size=1),
)
def test_text_to_speech_propagation(text: str, voice_id: str):
    """**Feature: education-audio-page, Property 8: Voice Selection Propagation**
    
    Validates that the voice_id and text specific parameters are correctly propagated 
    to the underlying ElevenLabs client during text_to_speech calls.
    """
    with patch("backend.services.elevenlabs_service.ElevenLabs") as MockElevenLabs:
        # Setup mock
        mock_client = MockElevenLabs.return_value
        # Mock convert to return a generator of bytes
        mock_client.text_to_speech.convert.return_value = (b"chunk1", b"chunk2")
        
        service = ElevenLabsService()
        result = service.text_to_speech(text=text, voice_id=voice_id)
        
        # Verify the call to the client
        mock_client.text_to_speech.convert.assert_called_once()
        call_args = mock_client.text_to_speech.convert.call_args
        
        # Verify arguments
        assert call_args.kwargs["voice_id"] == voice_id
        assert call_args.kwargs["text"] == text
        assert call_args.kwargs["model_id"] == "eleven_v3"
        
        # Verify result is concatenated bytes
        assert result == b"chunk1chunk2"
