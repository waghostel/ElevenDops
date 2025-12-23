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
        document_type="Guide",
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

@pytest.fixture
def mock_client():
    client = MagicMock()
    client.get_knowledge_documents = AsyncMock(return_value=MOCK_DOCS)
    client.get_available_voices = AsyncMock(return_value=MOCK_VOICES)
    client.generate_script = AsyncMock(return_value=MOCK_SCRIPT)
    client.get_audio_files = AsyncMock(return_value=[])
    client.health_check = AsyncMock(return_value={"status": "ok"})
    return client

def test_configuration_persistence(mock_client):
    """Property 1: Configuration Persistence."""
    with patch("streamlit_app.services.backend_api.get_backend_client", return_value=mock_client):
        at = AppTest.from_file("streamlit_app/pages/3_Education_Audio.py", default_timeout=30)
        at.session_state["IS_TESTING_BACKEND"] = True
        at.run()
        
        # Verify default model is gemini-2.5-flash
        # Find the model selectbox. It's inside Script Editor.
        # It has label "AI Model".
        # Note: Depending on column rendering, index might vary.
        # But we can find by label.
        
        # Select document first to show script editor
        at.selectbox[0].select_index(0).run()
        
        # Now 2 selectboxes: Doc, Model.
        assert len(at.selectbox) >= 2
        model_sb = at.selectbox[1]
        assert model_sb.label == "AI Model"
        assert model_sb.value == "gemini-2.5-flash"
        
        # Change selection
        model_sb.select("gemini-2.5-pro").run()
        
        # Rerun simply by calling run()? 
        # Actually modifying a widget triggers a rerun.
        
        assert at.selectbox[1].value == "gemini-2.5-pro"
        assert at.session_state.selected_llm_model == "gemini-2.5-pro"

def test_script_generation_parameters(mock_client):
    """Verify parameters passed to backend."""
    with patch("streamlit_app.services.backend_api.get_backend_client", return_value=mock_client):
        at = AppTest.from_file("streamlit_app/pages/3_Education_Audio.py", default_timeout=30)
        at.session_state["IS_TESTING_BACKEND"] = True
        at.run()
        
        # Select Doc
        at.selectbox[0].select_index(0).run()
        
        # Select Model
        at.selectbox[1].select("gemini-2.0-flash").run()
        
        # Set custom prompt directly in session state since dialog testing is hard
        at.session_state.custom_prompt = "My custom prompt"
        at.run()
        
        # Click Generate
        at.button(key="generate_script_btn").click().run()
        
        # Check backend call
        mock_client.generate_script.assert_called_with(
            knowledge_id="doc_1",
            model_name="gemini-2.0-flash",
            custom_prompt="My custom prompt"
        )
