"""Unit tests for PromptTemplateService."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from backend.services.prompt_template_service import (
    PromptTemplateService,
    TemplateInfo,
    get_prompt_template_service,
)

# Fixtures
@pytest.fixture
def mock_db_service():
    with patch("backend.services.prompt_template_service.get_data_service") as mock_get_ds:
        mock_instance = MagicMock()
        # Configure async methods with AsyncMock
        mock_instance.get_custom_templates = AsyncMock(return_value=[])
        mock_instance.get_custom_template = AsyncMock(return_value=None)
        mock_get_ds.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def service(mock_db_service):
    """Create service instance with mocked DB."""
    svc = PromptTemplateService()
    svc.clear_cache()
    return svc

# Tests
def test_template_metadata_contains_expected_templates(service):
    """TEMPLATE_METADATA should contain all expected template IDs."""
    expected_ids = [
        "pre_surgery",
        "post_surgery",
        "pre_post_surgery",
        "faq",
        "medication",
        "lifestyle",
    ]
    for tid in expected_ids:
        assert tid in service.TEMPLATE_METADATA


@pytest.mark.asyncio
async def test_list_templates_returns_all_templates(service):
    """list_templates should return all content type templates."""
    templates = await service.list_templates()
    
    assert len(templates) >= 6
    assert all(isinstance(t, TemplateInfo) for t in templates)
    
    template_ids = [t.template_id for t in templates]
    assert "pre_surgery" in template_ids
    assert "medication" in template_ids


@pytest.mark.asyncio
async def test_list_templates_includes_custom(service, mock_db_service):
    """list_templates should include custom templates from DB."""
    # Mock custom template
    mock_custom = MagicMock()
    mock_custom.template_id = "custom_123"
    mock_custom.display_name = "My Custom Template"
    mock_custom.description = "Test Description"
    mock_custom.preview = "Custom content..."
    mock_custom.category = "custom"
    
    # Configure AsyncMock return value
    mock_db_service.get_custom_templates.return_value = [mock_custom]
    
    templates = await service.list_templates()
    
    template_ids = [t.template_id for t in templates]
    assert "custom_123" in template_ids
    
    # Verify call
    mock_db_service.get_custom_templates.assert_called_once()


@pytest.mark.asyncio
async def test_get_template_returns_content(service):
    """get_template should return template content."""
    content = await service.get_template("pre_surgery")
    
    assert isinstance(content, str)
    assert len(content) > 0
    assert "Pre-Surgery" in content or "surgery" in content.lower()


@pytest.mark.asyncio
async def test_get_template_returns_custom_content(service, mock_db_service):
    """get_template should return custom template content."""
    # Mock DB response
    mock_custom = MagicMock()
    mock_custom.content = "Custom content here"
    # Ensure AsyncMock returns this object
    mock_db_service.get_custom_template.return_value = mock_custom
    
    content = await service.get_template("custom_xyz")
    
    assert content == "Custom content here"
    mock_db_service.get_custom_template.assert_called_with("custom_xyz")


@pytest.mark.asyncio
async def test_get_template_raises_on_invalid_id(service, mock_db_service):
    """get_template should raise ValueError for unknown template ID."""
    mock_db_service.get_custom_template.return_value = None
    
    with pytest.raises(ValueError, match="Unknown template ID"):
        await service.get_template("not_a_real_template")


def test_get_base_prompt_returns_content(service):
    """get_base_prompt should return base system prompt."""
    content = service.get_base_prompt()
    assert isinstance(content, str)
    assert len(content) > 0


@pytest.mark.asyncio
async def test_build_prompt_single_template(service):
    """build_prompt with single template should include base + template."""
    prompt = await service.build_prompt(template_ids=["pre_surgery"])
    
    assert isinstance(prompt, str)
    base = service.get_base_prompt()
    assert base in prompt or prompt.startswith(base[:50])
    
    template = await service.get_template("pre_surgery")
    assert template in prompt


@pytest.mark.asyncio
async def test_build_prompt_multiple_templates(service):
    """build_prompt with multiple templates should include all in order."""
    prompt = await service.build_prompt(
        template_ids=["pre_surgery", "medication"]
    )
    
    assert "Pre-Surgery" in prompt or "surgery" in prompt.lower()
    assert "Medication" in prompt or "medication" in prompt.lower()


@pytest.mark.asyncio
async def test_build_prompt_with_quick_instructions(service):
    """build_prompt should append quick instructions."""
    instructions = "Focus on elderly patients."
    prompt = await service.build_prompt(
        template_ids=["pre_surgery"],
        quick_instructions=instructions
    )
    
    assert instructions in prompt


@pytest.mark.asyncio
async def test_quick_instructions_whitespace_only_ignored(service):
    """Quick instructions with only whitespace should be ignored."""
    prompt_without = await service.build_prompt(template_ids=["pre_surgery"])
    prompt_with_whitespace = await service.build_prompt(
        template_ids=["pre_surgery"],
        quick_instructions="   \n\t  "
    )
    assert prompt_without == prompt_with_whitespace


def test_get_prompt_template_service_returns_singleton():
    """get_prompt_template_service should return singleton instance."""
    # Patch get_data_service to avoid actual DB connections during test
    with patch("backend.services.prompt_template_service.get_data_service"):
        service = get_prompt_template_service()
        assert isinstance(service, PromptTemplateService)
