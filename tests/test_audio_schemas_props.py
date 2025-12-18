"""Property tests for audio schemas."""

from datetime import datetime

from hypothesis import given
from hypothesis import strategies as st

from backend.models.schemas import (
    AudioGenerateRequest,
    AudioGenerateResponse,
    AudioListResponse,
    AudioMetadata,
    ScriptGenerateRequest,
    ScriptGenerateResponse,
    VoiceOption,
)


@given(st.text(min_size=1))
def test_script_generate_request_validation(knowledge_id: str):
    """Test ScriptGenerateRequest validation."""
    request = ScriptGenerateRequest(knowledge_id=knowledge_id)
    assert request.knowledge_id == knowledge_id


@given(
    st.text(min_size=1),
    st.text(min_size=1),
    st.datetimes(),
)
def test_script_generate_response_validation(script: str, knowledge_id: str, generated_at: datetime):
    """Test ScriptGenerateResponse validation."""
    response = ScriptGenerateResponse(
        script=script, knowledge_id=knowledge_id, generated_at=generated_at
    )
    assert response.script == script
    assert response.knowledge_id == knowledge_id
    assert response.generated_at == generated_at


@given(
    st.text(min_size=1),
    st.text(min_size=1, max_size=50000),
    st.text(min_size=1),
)
def test_audio_generate_request_validation(knowledge_id: str, script: str, voice_id: str):
    """Test AudioGenerateRequest validation."""
    request = AudioGenerateRequest(knowledge_id=knowledge_id, script=script, voice_id=voice_id)
    assert request.knowledge_id == knowledge_id
    assert request.script == script
    assert request.voice_id == voice_id


@given(
    st.text(min_size=1, max_size=50000),  # script first to match hypothesis strategy order if needed? No, order doesn't matter for args
    st.text(min_size=1),  # audio_id
    st.text(min_size=1),  # audio_url
    st.text(min_size=1),  # knowledge_id
    st.text(min_size=1),  # voice_id
    st.one_of(st.floats(min_value=0.1), st.none()),
    st.datetimes(),
)
def test_audio_generate_response_validity(
    script: str,
    audio_id: str,
    audio_url: str,
    knowledge_id: str,
    voice_id: str,
    duration_seconds: float | None,
    created_at: datetime,
):
    """**Feature: education-audio-page, Property 4: Successful Response Display** (Validation only)
    
    Validates that a successful response (AudioGenerateResponse) can be instantiated from valid data,
    representing the backend's ability to structure the response that the frontend will display.
    """
    response = AudioGenerateResponse(
        audio_id=audio_id,
        audio_url=audio_url,
        knowledge_id=knowledge_id,
        voice_id=voice_id,
        duration_seconds=duration_seconds,
        script=script,
        created_at=created_at,
    )
    assert response.audio_id == audio_id
    assert response.script == script
    # Serialization check
    json_data = response.model_dump()
    assert json_data["audio_id"] == audio_id


@given(
    st.text(min_size=1),
    st.text(min_size=1),
    st.one_of(st.text(min_size=1), st.none()),
    st.one_of(st.text(min_size=1), st.none()),
)
def test_voice_option_validation(
    voice_id: str,
    name: str,
    description: str | None,
    preview_url: str | None,
):
    """Test VoiceOption validation."""
    voice = VoiceOption(
        voice_id=voice_id,
        name=name,
        description=description,
        preview_url=preview_url,
    )
    assert voice.voice_id == voice_id
    assert voice.name == name
