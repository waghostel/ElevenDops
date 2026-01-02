from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from streamlit.testing.v1 import AppTest
from datetime import datetime
from streamlit_app.services.models import (
    AudioResponse,
    KnowledgeDocument,
    ScriptResponse,
    VoiceOption,
)

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

MOCK_SCRIPT = ScriptResponse(
    script="Generated script",
    knowledge_id="doc_1",
    generated_at=datetime.utcnow(),
    model_used="gemini-2.5-flash"
)

MOCK_VOICES = []

MOCK_SCRIPT_CONTENT = "Generated script"

async def mock_script_stream(*args, **kwargs):
    yield {"type": "token", "content": MOCK_SCRIPT_CONTENT}
    yield {"type": "complete", "script": MOCK_SCRIPT_CONTENT, "model_used": "gemini-2.5-flash-lite"}

@pytest.fixture
def mock_client():
    client = MagicMock()
    client.get_knowledge_documents = AsyncMock(return_value=MOCK_DOCS)
    client.get_available_voices = AsyncMock(return_value=MOCK_VOICES)
    # Mock the stream method instead of the sync/async value method
    client.generate_script_stream = MagicMock(side_effect=mock_script_stream)
    client.generate_script_stream = MagicMock(side_effect=mock_script_stream)
    client.get_audio_files = AsyncMock(return_value=[])
    client.get_templates = AsyncMock(return_value=[])
    client.health_check = AsyncMock(return_value={"status": "ok"})
    return client

def test_configuration_persistence(mock_client):
    """Property 1: Configuration Persistence."""
    with patch("streamlit_app.services.backend_api.get_backend_client", return_value=mock_client), \
         patch("streamlit_app.services.cached_data.get_documents_cached", return_value=MOCK_DOCS):
        at = AppTest.from_file("streamlit_app/pages/3_Education_Audio.py", default_timeout=30)
        at.session_state["IS_TESTING_BACKEND"] = True
        at.run()
        
        # Verify default model is gemini-2.5-flash-lite (per index=1 default)
        
        # Select document first to show script editor
        at.selectbox[0].select_index(0).run()
        
        # Now 2+ selectboxes: Doc, Speech Duration, AI Model.
        assert len(at.selectbox) >= 2
        
        # Find AI Model selectbox
        model_sb = next((sb for sb in at.selectbox if sb.label == "AI Model"), None)
        assert model_sb is not None, "AI Model selectbox not found"
        assert model_sb.value == "gemini-2.5-flash-lite"
        
        # Change selection to a valid option
        model_sb.select("gemini-3-flash-preview").run()
        
        # Re-fetch the selectbox after run
        model_sb = next((sb for sb in at.selectbox if sb.label == "AI Model"), None)
        assert model_sb.value == "gemini-3-flash-preview"
        assert at.session_state.selected_llm_model == "gemini-3-flash-preview"

def test_script_generation_parameters(mock_client):
    """Verify parameters passed to backend."""
    with patch("streamlit_app.services.backend_api.get_backend_client", return_value=mock_client), \
         patch("streamlit_app.services.cached_data.get_documents_cached", return_value=MOCK_DOCS):
        at = AppTest.from_file("streamlit_app/pages/3_Education_Audio.py", default_timeout=30)
        at.session_state["IS_TESTING_BACKEND"] = True
        at.run()
        
        # Select Doc
        at.selectbox[0].select_index(0).run()
        
        # Select Model (valid option)
        model_sb = next((sb for sb in at.selectbox if sb.label == "AI Model"), None)
        assert model_sb is not None, "AI Model selectbox not found"
        model_sb.select("gemini-3-pro-preview").run()
        
        # Set custom prompt directly in session state since dialog testing is hard
        at.session_state.custom_prompt = "My custom prompt"
        # Disable template mode to ensure custom prompt is used
        at.session_state.use_template_mode = False
        at.run()
        
        # Click Generate
        at.button(key="generate_script_btn").click().run()
        
        # Check backend call - assert on generate_script_stream
        mock_client.generate_script_stream.assert_called_with(
            knowledge_id="doc_1",
            model_name="gemini-3-pro-preview",
            custom_prompt="My custom prompt",
            template_ids=None,
            quick_instructions=None,
            system_prompt_override=None,
            preferred_languages=None,
            speaker1_languages=None,
            speaker2_languages=None,
            target_duration_minutes=None,
            is_multi_speaker=False
        )
