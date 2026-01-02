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
        tags=["Guide"],
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

MOCK_SCRIPT_CONTENT = "Generated script"

async def mock_script_stream(*args, **kwargs):
    yield {"type": "token", "content": MOCK_SCRIPT_CONTENT}
    yield {"type": "complete", "script": MOCK_SCRIPT_CONTENT, "model_used": "gemini-2.5-flash-lite"}

@pytest.fixture
def mock_client():
    client = MagicMock()
    client.get_knowledge_documents = AsyncMock(return_value=MOCK_DOCS)
    client.get_available_voices = AsyncMock(return_value=MOCK_VOICES)
    # Mock the stream method
    client.generate_script_stream = MagicMock(side_effect=mock_script_stream)
    client.generate_audio = AsyncMock(return_value=MOCK_AUDIO)
    client.get_audio_files = AsyncMock(return_value=[MOCK_AUDIO])
    client.get_templates = AsyncMock(return_value=[])
    client.health_check = AsyncMock(return_value={"status": "ok"})
    return client

def test_page_loads_and_displays_documents(mock_client):
    """Test that the page loads and fetches documents."""
    with patch("streamlit_app.services.backend_api.get_backend_client", return_value=mock_client), \
         patch("streamlit_app.services.cached_data.get_documents_cached", return_value=MOCK_DOCS):
        at = AppTest.from_file("streamlit_app/pages/3_Education_Audio.py", default_timeout=30)
        at.session_state["IS_TESTING_BACKEND"] = True
        at.run()
        
        assert not at.exception
        # Check title
        assert "Patient Education Audio" in at.title[0].value
        # Check document selector options matches mockup
        assert "Flu" in at.selectbox[0].options

def test_script_generation_flow(mock_client):
    """Test selecting a document and generating a script."""
    with patch("streamlit_app.services.backend_api.get_backend_client", return_value=mock_client), \
         patch("streamlit_app.services.cached_data.get_documents_cached", return_value=MOCK_DOCS):
        at = AppTest.from_file("streamlit_app/pages/3_Education_Audio.py", default_timeout=30)
        at.session_state["IS_TESTING_BACKEND"] = True
        at.run()
        
        # Select document "Flu" at index 0
        at.selectbox[0].select_index(0).run()
        
        # Check raw content expanded
        assert "Flu guide content" in at.markdown[1].value
        
        # Click Generate Script button
        at.button(key="generate_script_btn").click().run()
        
        # Verify script appears in text area
        assert at.text_area(key="script_editor_area_1").value == "Generated script"
        
        # Verify audio generation section appears (check for AI Model or Duration)
        # We check for AI Model which is in the script editor section
        model_sb = next((sb for sb in at.selectbox if sb.label == "AI Model"), None)
        assert model_sb is not None, "AI Model selectbox not found"
        
        # Verify client call
        mock_client.generate_script_stream.assert_called_with(
            knowledge_id="doc_1",
            model_name="gemini-2.5-flash-lite",
            custom_prompt=None,
            template_ids=["pre_surgery"],
            quick_instructions="",
            system_prompt_override=None,
            preferred_languages=[],
            speaker1_languages=None,
            speaker2_languages=None,
            target_duration_minutes=3,
            is_multi_speaker=False
        )

def test_audio_generation_flow(mock_client):
    """Test selecting a voice and generating audio."""
    with patch("streamlit_app.services.backend_api.get_backend_client", return_value=mock_client), \
         patch("streamlit_app.services.cached_data.get_documents_cached", return_value=MOCK_DOCS), \
         patch("streamlit_app.services.cached_data.get_voices_cached", return_value=MOCK_VOICES):
        at = AppTest.from_file("streamlit_app/pages/3_Education_Audio.py", default_timeout=30)
        at.session_state["IS_TESTING_BACKEND"] = True
        at.run()
        
        # 1. Select Document
        doc_sb = next((sb for sb in at.selectbox if "Choose a condition" in sb.label), None)
        assert doc_sb, "Document selector not found"
        doc_sb.select_index(0).run()
        
        # 2. Generate Script
        at.button(key="generate_script_btn").click().run()
        
        # 3. Select Voice
        # Voice selector should now be visible
        assert not at.error, f"Errors: {[e.value for e in at.error]}"
        assert not at.warning, f"Warnings: {[w.value for w in at.warning]}"
        
        # Find Speaker 1 Voice selectbox
        voice_sb = next((sb for sb in at.selectbox if sb.label == "Speaker 1 Voice"), None)
        assert voice_sb is not None, "Speaker 1 Voice selectbox not found"
        
        # "Rachel" is at index 0 of the voices list (mocked)
        voice_sb.select("Rachel").run()
        
        # 4. Generate Audio
        audio_btn = at.button(key="generate_audio_btn")
        assert audio_btn, "Audio button missing"
        audio_btn.click().run()
        
        # Verify client call
        mock_client.generate_audio.assert_called()
        call_args = mock_client.generate_audio.call_args
        assert call_args[0][0] == "doc_1"
        assert call_args[0][1] == "Generated script" # From MOCK_SCRIPT_CONTENT
        assert call_args[0][2] == "v1"

def test_reset_on_document_change(mock_client):
    """Test that state resets when document selection changes."""
    with patch("streamlit_app.services.backend_api.get_backend_client", return_value=mock_client), \
         patch("streamlit_app.services.cached_data.get_documents_cached", return_value=MOCK_DOCS):
        at = AppTest.from_file("streamlit_app/pages/3_Education_Audio.py", default_timeout=30)
        at.session_state["IS_TESTING_BACKEND"] = True
        at.run()
        
        # Setup initial state
        at.selectbox[0].select_index(0).run()
        at.button(key="generate_script_btn").click().run()
        
        # Verify script
        assert at.text_area(key="script_editor_area_1").value == "Generated script"
        
        # Change document
        # To test doc change, we need the page to reload with new docs.
        # But AppTest is persistent. If we change what get_documents_cached returns, 
        # normally cache would prevent reload unless we clear it.
        # But since we are patching the cached function, subsequent calls might return new value
        # IF the cache logic in wrapper is bypassed or we patch again.
        
        # Actually, in AppTest, calling run() again re-executes the script.
        # But the patch context manager might exit if we are not careful?
        # No, we are inside `with patch` block.
        
        # Update what the patch returns?
        # mock_client.get_knowledge_documents was used before.
        # Now we need to update the return_value of the patch for get_documents_cached?
        # That's tricky with the current structure.
        
        # Let's just create a new list for the second part.
        doc2 = replace(MOCK_DOCS[0], knowledge_id="doc_2", disease_name="Cold")
        new_docs = [MOCK_DOCS[0], doc2]
        
        # Note: patch(...) returns a Mock object.
        # But here we used return_value=MOCK_DOCS in the constructor.
        # To change it dynamically, we should start the patch, get the mock, and configure it.
        pass

    # Re-writing the test logic to support dynamic return values
    with patch("streamlit_app.services.backend_api.get_backend_client", return_value=mock_client):
        # We need to control cached_data mock
        with patch("streamlit_app.services.cached_data.get_documents_cached") as mock_get_docs:
            mock_get_docs.return_value = MOCK_DOCS
            
            at = AppTest.from_file("streamlit_app/pages/3_Education_Audio.py", default_timeout=30)
            at.session_state["IS_TESTING_BACKEND"] = True
            at.run()
            
            # Setup initial state
            at.selectbox[0].select_index(0).run()
            at.button(key="generate_script_btn").click().run()
             
            # Verify script
            assert at.text_area(key="script_editor_area_1").value == "Generated script"
            
            # Change document
            doc2 = replace(MOCK_DOCS[0], knowledge_id="doc_2", disease_name="Cold")
            new_docs = [MOCK_DOCS[0], doc2]
            mock_get_docs.return_value = new_docs
            
            # Trigger a rerun or re-selection?
            # Ideally streamlit cache would hold old value.
            # But here we mocked the cached function itself.
            # Does calling at.run() trigger a re-fetch?
            # Only if cache invalidates?
            # Actually st.cache_data logic is IN the decorator.
            # If we patch the function `get_documents_cached` in `cached_data` module,
            # we are patching the DECORATED function if it was already decorated at import time?
            # Yes, imports happen at top level.
            # `from streamlit_app.services.cached_data import get_documents_cached` imports the decorated object.
            # `patch` replaces that object with a MagicMock.
            # So the decorator logic (st.cache_data) IS LOST.
            # Use `patch` replaces the object in the target module.
            # If we patch `streamlit_app.services.cached_data.get_documents_cached`, we replace the decorated function with a plain Mock.
            # So it will behave like a regular function call (no caching behavior in test, which is fine, usually better).
            
            # So updating return_value should work on next call.
            at.run() # Rerun script to pick up new docs?
            
            # Select "Cold"
            # Docs: "Flu", "Cold"
            # "Flu" was selected.
            at.selectbox[0].select("Cold").run()
            
            # Script area should be empty (reset)
            # Filter for the specific key - key increments on reset to force clear
            script_areas = [ta for ta in at.text_area if ta.key == "script_editor_area_2"]
            assert len(script_areas) == 1, "Script text area should be present"
            assert script_areas[0].value == "", "Script text area should be empty"
