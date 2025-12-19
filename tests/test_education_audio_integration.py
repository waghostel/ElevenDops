"""Integration tests for Education Audio Page."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from streamlit.testing.v1 import AppTest

from streamlit_app.services.models import (
    AudioResponse,
    KnowledgeDocument,
    ScriptResponse,
    VoiceOption,
)
from dataclasses import replace
from datetime import datetime

# Mock Data
MOCK_DOCS = [
    KnowledgeDocument(
        knowledge_id="doc_1",
        doctor_id="doc",
        disease_name="Flu",
        document_type="Guide",
        raw_content="Flu guide content",
        sync_status="COMPLETED",
        elevenlabs_document_id="el_1",
        structured_sections={},
        created_at=datetime.utcnow()
    )
]

MOCK_VOICES = [
    VoiceOption(voice_id="v1", name="Rachel", description="American, calm", preview_url="https://example.com/preview1.mp3"),
    VoiceOption(voice_id="v2", name="Drew", description="British, news", preview_url="https://example.com/preview2.mp3"),
]

MOCK_SCRIPT = ScriptResponse(
    script="Generated script",
    knowledge_id="doc_1",
    generated_at=datetime.utcnow()
)

MOCK_AUDIO = AudioResponse(
    audio_id="aud_1",
    audio_url="http://audio.url",
    knowledge_id="doc_1",
    voice_id="v1",
    duration_seconds=10.0,
    script="Generated script",
    created_at=datetime.utcnow()
)

@pytest.fixture
def mock_client():
    client = MagicMock()
    client.get_knowledge_documents = AsyncMock(return_value=MOCK_DOCS)
    client.get_available_voices = AsyncMock(return_value=MOCK_VOICES)
    client.generate_script = AsyncMock(return_value=MOCK_SCRIPT)
    client.generate_audio = AsyncMock(return_value=MOCK_AUDIO)
    client.get_audio_files = AsyncMock(return_value=[MOCK_AUDIO])
    return client

def test_page_loads_and_displays_documents(mock_client):
    """Test that the page loads and fetches documents."""
    with patch("streamlit_app.services.backend_api.get_backend_client", return_value=mock_client):
        at = AppTest.from_file("streamlit_app/pages/3_Education_Audio.py")
        at.run()
        
        assert not at.exception
        # Check title
        assert "Patient Education Audio" in at.title[0].value
        # Check document selector options matches mockup
        assert "Flu" in at.selectbox[0].options

def test_script_generation_flow(mock_client):
    """Test selecting a document and generating a script."""
    with patch("streamlit_app.services.backend_api.get_backend_client", return_value=mock_client):
        at = AppTest.from_file("streamlit_app/pages/3_Education_Audio.py")
        at.run()
        
        # Select document "Flu" at index 0
        at.selectbox[0].select_index(0).run()
        
        # Check raw content expanded
        assert "Flu guide content" in at.markdown[1].value
        
        # Click Generate Script button
        at.button(key="generate_script_btn").click().run()
        
        # Verify script appears in text area
        # Check using key if possible, but index 0 is likely still correct if only 1 text area
        assert at.text_area(key="script_editor_area").value == "Generated script"
        
        # Verify audio generation section appears (2nd selectbox)
        assert len(at.selectbox) >= 2, f"Audio section not rendered. Selectboxes: {len(at.selectbox)}"
        
        # Verify client call
        mock_client.generate_script.assert_called_with("doc_1")

def test_audio_generation_flow(mock_client):
    """Test selecting a voice and generating audio."""
    with patch("streamlit_app.services.backend_api.get_backend_client", return_value=mock_client):
        at = AppTest.from_file("streamlit_app/pages/3_Education_Audio.py")
        at.run()
        
        # 1. Select Document
        at.selectbox[0].select_index(0).run()
        
        # 2. Generate Script
        at.button(key="generate_script_btn").click().run()
        
        # 3. Select Voice
        # Voice selector should now be visible (index 1)
        assert not at.error, f"Errors: {[e.value for e in at.error]}"
        assert not at.warning, f"Warnings: {[w.value for w in at.warning]}"
        
        assert len(at.selectbox) >= 2
        # "Rachel" is at index 0 of the voices list (mocked)
        at.selectbox[1].select("Rachel").run()
        
        # 4. Generate Audio
        audio_btn = at.button(key="generate_audio_btn")
        assert audio_btn, "Audio button missing"
        audio_btn.click().run()
        
        # Verify client call
        mock_client.generate_audio.assert_called()
        call_args = mock_client.generate_audio.call_args
        assert call_args[0][0] == "doc_1"
        assert call_args[0][1] == "Generated script" # From MOCK_SCRIPT
        assert call_args[0][2] == "v1"

def test_reset_on_document_change(mock_client):
    """Test that state resets when document selection changes."""
    with patch("streamlit_app.services.backend_api.get_backend_client", return_value=mock_client):
        at = AppTest.from_file("streamlit_app/pages/3_Education_Audio.py")
        at.run()
        
        # Setup initial state
        at.selectbox[0].select_index(0).run()
        at.button(key="generate_script_btn").click().run()
        
        # Verify script
        assert at.text_area(key="script_editor_area").value == "Generated script"
        
        # Change document
        # Update mock to include a second document
        doc2 = replace(MOCK_DOCS[0], knowledge_id="doc_2", disease_name="Cold")
        mock_client.get_knowledge_documents.return_value = [MOCK_DOCS[0], doc2]
        
        at = AppTest.from_file("streamlit_app/pages/3_Education_Audio.py")
        with patch("streamlit_app.services.backend_api.get_backend_client", return_value=mock_client):
             at.run()
             # Select first
             at.selectbox[0].select("Flu").run()
             
             at.button(key="generate_script_btn").click().run()
             assert at.text_area(key="script_editor_area").value == "Generated script"
             
             # Select second
             at.selectbox[0].select("Cold").run()
             
             # Script area should be gone or empty
             # render_script_editor checks if session_state.selected_document, which it is.
             # render_audio_generation checks if generated_script.
             # If logic works, generated_script is reset to "".
             # But render_script_editor renders text_area ONLY if generated_script is truthy.
             
             # So text_area should be missing or empty?
             # My code: if st.session_state.generated_script: st.text_area(...)
             
             # So if reset works, text_area should NOT exist.
             # Or len(at.text_area(key="script_editor_area")) should be failure or None?
             
             # AppTest accessor returns valid wrapper or empty?
             # accessing at.text_area(key="...") returns an element wrapper.
             # wrapper.value might raise if doesn't exist? Or return defaults?
             # len(at.text_area) checks ALL text areas.
             
             assert len(at.text_area) == 0, f"Text area should be gone. Found {len(at.text_area)}"
