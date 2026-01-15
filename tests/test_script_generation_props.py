import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import AsyncMock, patch, MagicMock
from backend.services.script_generation_service import ScriptGenerationService
import datetime


@given(
    model_name=st.sampled_from(["gemini-2.5-flash-lite", "gemini-3-flash-preview", "gemini-3-pro-preview"]),
    prompt=st.text(min_size=1, max_size=100),
    content=st.text(min_size=1, max_size=100)
)
@pytest.mark.asyncio
async def test_configuration_passthrough(model_name, prompt, content):
    """Property 2: Configuration Passthrough.
    Verify that model_name and prompt are correctly passed to the LLM.
    """
    with patch("backend.services.langgraph_workflow.ChatGoogleGenerativeAI") as mock_llm_cls:
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = MagicMock(content="Generated Script")
        mock_llm_cls.return_value = mock_llm
        
        with patch("backend.services.langgraph_workflow.get_settings") as mock_settings:
            # Emulate having an API key so it tries to call LLM
            mock_settings.return_value.google_api_key = "fake_key"
            mock_settings.return_value.use_mock_data = False
            
            service = ScriptGenerationService()
            # Run generation
            await service.generate_script(content, model_name, prompt)
            
            # Check LLM initialization
            mock_llm_cls.assert_called()
            call_kwargs = mock_llm_cls.call_args.kwargs
            assert call_kwargs["model"] == model_name
            assert call_kwargs["google_api_key"] == "fake_key"
            
            # Check prompt passing
            mock_llm.ainvoke.assert_called_once()
            messages = mock_llm.ainvoke.call_args[0][0]
            # messages[0] should be SystemMessage with prompt
            assert messages[0].content == prompt
            # messages[1] should be HumanMessage with content
            assert content in messages[1].content



@given(
    content=st.text(min_size=1),
    generated_text=st.text(min_size=1, max_size=500)
)
@pytest.mark.asyncio
async def test_successful_response_format(content, generated_text):
    """Property 3: Successful Response Format.
    Verify that the result contains the script and correct metadata.
    """
    with patch("backend.services.langgraph_workflow.ChatGoogleGenerativeAI") as mock_llm_cls:
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = MagicMock(content=generated_text)
        mock_llm_cls.return_value = mock_llm
        
        with patch("backend.services.langgraph_workflow.get_settings") as mock_settings:
            mock_settings.return_value.google_api_key = "fake_key"
            mock_settings.return_value.use_mock_data = False
            
            service = ScriptGenerationService()
            result = await service.generate_script(content, "gemini-3-flash-preview", "prompt")
            
            # post_process_node might strip whitespace
            assert result["script"] == generated_text.strip()
            assert result["model_used"] == "gemini-3-flash-preview"
            assert isinstance(result["generated_at"], datetime.datetime)
            assert result["error"] is None



@given(error_msg=st.text(min_size=1))
@pytest.mark.asyncio
async def test_error_propagation(error_msg):
    """Property 4: Error Propagation.
    Verify that exceptions during generation are propagated.
    """
    with patch("backend.services.langgraph_workflow.ChatGoogleGenerativeAI") as mock_llm_cls:
        mock_llm = AsyncMock()
        mock_llm.ainvoke.side_effect = Exception(error_msg)
        mock_llm_cls.return_value = mock_llm
        
        with patch("backend.services.langgraph_workflow.get_settings") as mock_settings:
            mock_settings.return_value.google_api_key = "fake_key"
            mock_settings.return_value.use_mock_data = False
            
            service = ScriptGenerationService()
            with pytest.raises(Exception) as excinfo:
                await service.generate_script("content", "model", "prompt")
            
            assert error_msg in str(excinfo.value)
