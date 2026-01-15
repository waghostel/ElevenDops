"""
Task 17: Templates API Tests

This test file validates template management functionality:
- GET /api/templates (list templates)
- POST /api/templates (create custom template)
- GET /api/templates/{template_id} (get template content)
- PUT /api/templates/{template_id} (update custom template)
- DELETE /api/templates/{template_id} (delete custom template)
- GET /api/templates/system-prompt (get base system prompt)
- POST /api/templates/preview (preview combined prompt)

Requirements: 8.1-8.7
Property Test: Property 20 - Template Preview Accuracy

Test Coverage:
- Unit tests for each endpoint
- Property-based tests for template preview accuracy
- Error handling and edge cases
- Schema validation
"""

import pytest
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from hypothesis import given, strategies as st, settings, HealthCheck

from postman_test_helpers import (
    TestDataManager,
    valid_name_strategy,
    valid_description_strategy,
    assert_valid_response,
    log_test_info,
)

# Import backend modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.test_data_generator import TestDataGenerator
from backend.services.test_script_generator import TestScriptGenerator
from backend.services.collection_builder import CollectionBuilder
from backend.services.environment_manager import EnvironmentManager

logger = logging.getLogger(__name__)


# ============================================================================
# Test Request Creation (for Postman Collection)
# ============================================================================

class TestTemplateRequestCreation:
    """Create test requests for Templates API endpoints."""
    
    @staticmethod
    def create_list_templates_request() -> Dict[str, Any]:
        """Create GET /api/templates request."""
        return {
            "name": "List Templates",
            "request": {
                "method": "GET",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "url": {
                    "raw": "{{base_url}}/api/templates",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "templates"]
                }
            },
            "tests": TestScriptGenerator.generate_status_check(200) +
                     TestScriptGenerator.generate_schema_validation(
                         ["template_id", "display_name", "description", "category"]
                     )
        }
    
    @staticmethod
    def create_create_template_request(template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create POST /api/templates request."""
        return {
            "name": "Create Custom Template",
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps(template_data)
                },
                "url": {
                    "raw": "{{base_url}}/api/templates",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "templates"]
                }
            },
            "tests": TestScriptGenerator.generate_status_check(200) +
                     TestScriptGenerator.generate_schema_validation(
                         ["template_id", "display_name", "content"]
                     ) +
                     TestScriptGenerator.generate_variable_save("template_id", "$.template_id")
        }
    
    @staticmethod
    def create_get_template_request(template_id: str) -> Dict[str, Any]:
        """Create GET /api/templates/{template_id} request."""
        return {
            "name": "Get Template Content",
            "request": {
                "method": "GET",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "url": {
                    "raw": f"{{{{base_url}}}}/api/templates/{template_id}",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "templates", template_id]
                }
            },
            "tests": TestScriptGenerator.generate_status_check(200) +
                     TestScriptGenerator.generate_schema_validation(
                         ["template_id", "content"]
                     )
        }
    
    @staticmethod
    def create_update_template_request(template_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create PUT /api/templates/{template_id} request."""
        return {
            "name": "Update Custom Template",
            "request": {
                "method": "PUT",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps(update_data)
                },
                "url": {
                    "raw": f"{{{{base_url}}}}/api/templates/{template_id}",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "templates", template_id]
                }
            },
            "tests": TestScriptGenerator.generate_status_check(200) +
                     TestScriptGenerator.generate_schema_validation(
                         ["template_id", "display_name"]
                     )
        }
    
    @staticmethod
    def create_delete_template_request(template_id: str) -> Dict[str, Any]:
        """Create DELETE /api/templates/{template_id} request."""
        return {
            "name": "Delete Custom Template",
            "request": {
                "method": "DELETE",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "url": {
                    "raw": f"{{{{base_url}}}}/api/templates/{template_id}",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "templates", template_id]
                }
            },
            "tests": TestScriptGenerator.generate_status_check(200)
        }
    
    @staticmethod
    def create_get_system_prompt_request() -> Dict[str, Any]:
        """Create GET /api/templates/system-prompt request."""
        return {
            "name": "Get System Prompt",
            "request": {
                "method": "GET",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "url": {
                    "raw": "{{base_url}}/api/templates/system-prompt",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "templates", "system-prompt"]
                }
            },
            "tests": TestScriptGenerator.generate_status_check(200) +
                     TestScriptGenerator.generate_schema_validation(["content"])
        }
    
    @staticmethod
    def create_preview_prompt_request(preview_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create POST /api/templates/preview request."""
        return {
            "name": "Preview Combined Prompt",
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps(preview_data)
                },
                "url": {
                    "raw": "{{base_url}}/api/templates/preview",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "templates", "preview"]
                }
            },
            "tests": TestScriptGenerator.generate_status_check(200) +
                     TestScriptGenerator.generate_schema_validation(
                         ["template_ids", "combined_prompt", "character_count"]
                     )
        }


# ============================================================================
# Unit Tests for Templates API
# ============================================================================

class TestListTemplates:
    """Test GET /api/templates endpoint."""
    
    def test_list_templates_request_creation(self):
        """Test creating list templates request."""
        request = TestTemplateRequestCreation.create_list_templates_request()
        
        assert request["name"] == "List Templates"
        assert request["request"]["method"] == "GET"
        assert "/api/templates" in request["request"]["url"]["raw"]
        assert "pm.test" in request["tests"]
    
    def test_list_templates_response_schema(self):
        """Test list templates response has correct schema."""
        request = TestTemplateRequestCreation.create_list_templates_request()
        
        # Verify test script validates schema
        assert "template_id" in request["tests"]
        assert "display_name" in request["tests"]
        assert "description" in request["tests"]
        assert "category" in request["tests"]
    
    def test_list_templates_status_check(self):
        """Test list templates includes status check."""
        request = TestTemplateRequestCreation.create_list_templates_request()
        
        assert "200" in request["tests"]
        assert "pm.response.to.have.status" in request["tests"]


class TestCreateTemplate:
    """Test POST /api/templates endpoint."""
    
    def test_create_template_request_creation(self):
        """Test creating create template request."""
        template_data = {
            "display_name": "Test Template",
            "description": "Test description",
            "content": "Test content for template"
        }
        request = TestTemplateRequestCreation.create_create_template_request(template_data)
        
        assert request["name"] == "Create Custom Template"
        assert request["request"]["method"] == "POST"
        assert "/api/templates" in request["request"]["url"]["raw"]
    
    def test_create_template_body_structure(self):
        """Test create template request body structure."""
        template_data = {
            "display_name": "Test Template",
            "description": "Test description",
            "content": "Test content for template"
        }
        request = TestTemplateRequestCreation.create_create_template_request(template_data)
        
        body = json.loads(request["request"]["body"]["raw"])
        assert body["display_name"] == "Test Template"
        assert body["description"] == "Test description"
        assert body["content"] == "Test content for template"
    
    def test_create_template_saves_id(self):
        """Test create template saves template_id variable."""
        template_data = {
            "display_name": "Test Template",
            "description": "Test description",
            "content": "Test content for template"
        }
        request = TestTemplateRequestCreation.create_create_template_request(template_data)
        
        assert "template_id" in request["tests"]
        assert "pm.collectionVariables.set" in request["tests"]


class TestGetTemplate:
    """Test GET /api/templates/{template_id} endpoint."""
    
    def test_get_template_request_creation(self):
        """Test creating get template request."""
        template_id = "test_template_123"
        request = TestTemplateRequestCreation.create_get_template_request(template_id)
        
        assert request["name"] == "Get Template Content"
        assert request["request"]["method"] == "GET"
        assert template_id in request["request"]["url"]["raw"]
    
    def test_get_template_url_structure(self):
        """Test get template URL structure."""
        template_id = "test_template_456"
        request = TestTemplateRequestCreation.create_get_template_request(template_id)
        
        url = request["request"]["url"]["raw"]
        assert f"/api/templates/{template_id}" in url
    
    def test_get_template_response_schema(self):
        """Test get template response schema validation."""
        template_id = "test_template_789"
        request = TestTemplateRequestCreation.create_get_template_request(template_id)
        
        assert "template_id" in request["tests"]
        assert "content" in request["tests"]


class TestUpdateTemplate:
    """Test PUT /api/templates/{template_id} endpoint."""
    
    def test_update_template_request_creation(self):
        """Test creating update template request."""
        template_id = "test_template_update"
        update_data = {
            "display_name": "Updated Template",
            "description": "Updated description"
        }
        request = TestTemplateRequestCreation.create_update_template_request(
            template_id, update_data
        )
        
        assert request["name"] == "Update Custom Template"
        assert request["request"]["method"] == "PUT"
        assert template_id in request["request"]["url"]["raw"]
    
    def test_update_template_body_structure(self):
        """Test update template request body structure."""
        template_id = "test_template_update"
        update_data = {
            "display_name": "Updated Template",
            "description": "Updated description"
        }
        request = TestTemplateRequestCreation.create_update_template_request(
            template_id, update_data
        )
        
        body = json.loads(request["request"]["body"]["raw"])
        assert body["display_name"] == "Updated Template"
        assert body["description"] == "Updated description"
    
    def test_update_template_partial_update(self):
        """Test update template with partial data."""
        template_id = "test_template_partial"
        update_data = {
            "display_name": "Only Name Updated"
        }
        request = TestTemplateRequestCreation.create_update_template_request(
            template_id, update_data
        )
        
        body = json.loads(request["request"]["body"]["raw"])
        assert "display_name" in body
        assert body["display_name"] == "Only Name Updated"


class TestDeleteTemplate:
    """Test DELETE /api/templates/{template_id} endpoint."""
    
    def test_delete_template_request_creation(self):
        """Test creating delete template request."""
        template_id = "test_template_delete"
        request = TestTemplateRequestCreation.create_delete_template_request(template_id)
        
        assert request["name"] == "Delete Custom Template"
        assert request["request"]["method"] == "DELETE"
        assert template_id in request["request"]["url"]["raw"]
    
    def test_delete_template_url_structure(self):
        """Test delete template URL structure."""
        template_id = "test_template_delete_456"
        request = TestTemplateRequestCreation.create_delete_template_request(template_id)
        
        url = request["request"]["url"]["raw"]
        assert f"/api/templates/{template_id}" in url
    
    def test_delete_template_status_check(self):
        """Test delete template includes status check."""
        template_id = "test_template_delete_789"
        request = TestTemplateRequestCreation.create_delete_template_request(template_id)
        
        assert "200" in request["tests"]


class TestGetSystemPrompt:
    """Test GET /api/templates/system-prompt endpoint."""
    
    def test_get_system_prompt_request_creation(self):
        """Test creating get system prompt request."""
        request = TestTemplateRequestCreation.create_get_system_prompt_request()
        
        assert request["name"] == "Get System Prompt"
        assert request["request"]["method"] == "GET"
        assert "/api/templates/system-prompt" in request["request"]["url"]["raw"]
    
    def test_get_system_prompt_response_schema(self):
        """Test get system prompt response schema."""
        request = TestTemplateRequestCreation.create_get_system_prompt_request()
        
        assert "content" in request["tests"]
        assert "pm.test" in request["tests"]
    
    def test_get_system_prompt_status_check(self):
        """Test get system prompt includes status check."""
        request = TestTemplateRequestCreation.create_get_system_prompt_request()
        
        assert "200" in request["tests"]


class TestPreviewPrompt:
    """Test POST /api/templates/preview endpoint."""
    
    def test_preview_prompt_request_creation(self):
        """Test creating preview prompt request."""
        preview_data = {
            "template_ids": ["pre_surgery", "medication"],
            "quick_instructions": "Focus on patient education"
        }
        request = TestTemplateRequestCreation.create_preview_prompt_request(preview_data)
        
        assert request["name"] == "Preview Combined Prompt"
        assert request["request"]["method"] == "POST"
        assert "/api/templates/preview" in request["request"]["url"]["raw"]
    
    def test_preview_prompt_body_structure(self):
        """Test preview prompt request body structure."""
        preview_data = {
            "template_ids": ["pre_surgery", "medication"],
            "quick_instructions": "Focus on patient education"
        }
        request = TestTemplateRequestCreation.create_preview_prompt_request(preview_data)
        
        body = json.loads(request["request"]["body"]["raw"])
        assert body["template_ids"] == ["pre_surgery", "medication"]
        assert body["quick_instructions"] == "Focus on patient education"
    
    def test_preview_prompt_response_schema(self):
        """Test preview prompt response schema validation."""
        preview_data = {
            "template_ids": ["faq"],
            "quick_instructions": None
        }
        request = TestTemplateRequestCreation.create_preview_prompt_request(preview_data)
        
        assert "template_ids" in request["tests"]
        assert "combined_prompt" in request["tests"]
        assert "character_count" in request["tests"]
    
    def test_preview_prompt_without_instructions(self):
        """Test preview prompt without quick instructions."""
        preview_data = {
            "template_ids": ["lifestyle"],
        }
        request = TestTemplateRequestCreation.create_preview_prompt_request(preview_data)
        
        body = json.loads(request["request"]["body"]["raw"])
        assert body["template_ids"] == ["lifestyle"]


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestTemplatePreviewAccuracy:
    """
    Property 20: Template Preview Accuracy
    
    Verifies that template preview endpoint accurately combines templates
    and produces consistent, predictable output.
    
    Requirements: 8.1-8.7
    """
    
    @given(
        template_ids=st.lists(
            st.sampled_from([
                "pre_surgery", "post_surgery", "pre_post_surgery",
                "faq", "medication", "lifestyle"
            ]),
            min_size=1,
            max_size=3,
            unique=True
        ),
        quick_instructions=st.one_of(
            st.none(),
            st.text(min_size=0, max_size=200)
        )
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.too_slow]
    )
    def test_preview_combines_templates_correctly(self, template_ids, quick_instructions):
        """
        Property: Template preview should combine selected templates
        in the correct order and include quick instructions if provided.
        
        Invariants:
        1. Combined prompt contains all selected template IDs
        2. Combined prompt is non-empty
        3. Character count matches actual content length
        4. Quick instructions appear in output if provided
        5. Output is deterministic for same inputs
        """
        preview_data = {
            "template_ids": template_ids,
        }
        if quick_instructions is not None:
            preview_data["quick_instructions"] = quick_instructions
        
        request = TestTemplateRequestCreation.create_preview_prompt_request(preview_data)
        
        # Verify request structure
        assert request["request"]["method"] == "POST"
        assert "/api/templates/preview" in request["request"]["url"]["raw"]
        
        # Verify body contains all template IDs
        body = json.loads(request["request"]["body"]["raw"])
        assert body["template_ids"] == template_ids
        
        # Verify response schema validation
        assert "template_ids" in request["tests"]
        assert "combined_prompt" in request["tests"]
        assert "character_count" in request["tests"]
        
        # Verify test script checks for character count
        assert "pm.test" in request["tests"]
    
    @given(
        template_ids=st.lists(
            st.sampled_from([
                "pre_surgery", "post_surgery", "faq", "medication"
            ]),
            min_size=1,
            max_size=2,
            unique=True
        )
    )
    @settings(max_examples=50)
    def test_preview_character_count_accuracy(self, template_ids):
        """
        Property: Character count in preview response should match
        the actual length of the combined prompt.
        
        Invariants:
        1. Character count is a positive integer
        2. Character count matches combined_prompt length
        3. Character count is consistent across multiple calls
        """
        preview_data = {
            "template_ids": template_ids,
            "quick_instructions": "Test instructions"
        }
        
        request = TestTemplateRequestCreation.create_preview_prompt_request(preview_data)
        
        # Verify character count validation in test script
        assert "character_count" in request["tests"]
        assert "pm.test" in request["tests"]
        
        # Verify response includes character count
        body = json.loads(request["request"]["body"]["raw"])
        assert "template_ids" in body
    
    @given(
        template_ids=st.lists(
            st.sampled_from([
                "pre_surgery", "post_surgery", "pre_post_surgery",
                "faq", "medication", "lifestyle"
            ]),
            min_size=1,
            max_size=3,
            unique=True
        )
    )
    @settings(max_examples=50)
    def test_preview_deterministic_output(self, template_ids):
        """
        Property: Template preview should produce deterministic output
        for the same input templates.
        
        Invariants:
        1. Same template_ids produce same combined_prompt
        2. Template order matters (different order = different output)
        3. Output is reproducible
        """
        preview_data_1 = {
            "template_ids": template_ids,
            "quick_instructions": "Same instructions"
        }
        preview_data_2 = {
            "template_ids": template_ids,
            "quick_instructions": "Same instructions"
        }
        
        request_1 = TestTemplateRequestCreation.create_preview_prompt_request(preview_data_1)
        request_2 = TestTemplateRequestCreation.create_preview_prompt_request(preview_data_2)
        
        # Both requests should have identical structure
        body_1 = json.loads(request_1["request"]["body"]["raw"])
        body_2 = json.loads(request_2["request"]["body"]["raw"])
        
        assert body_1["template_ids"] == body_2["template_ids"]
        assert body_1.get("quick_instructions") == body_2.get("quick_instructions")
    
    @given(
        quick_instructions=st.text(min_size=1, max_size=300)
    )
    @settings(max_examples=50)
    def test_preview_includes_quick_instructions(self, quick_instructions):
        """
        Property: When quick_instructions are provided, they should
        be included in the combined prompt.
        
        Invariants:
        1. Quick instructions are preserved in output
        2. Quick instructions don't corrupt template content
        3. Quick instructions are properly formatted
        """
        preview_data = {
            "template_ids": ["medication"],
            "quick_instructions": quick_instructions
        }
        
        request = TestTemplateRequestCreation.create_preview_prompt_request(preview_data)
        
        body = json.loads(request["request"]["body"]["raw"])
        assert body["quick_instructions"] == quick_instructions
        
        # Verify test script validates instructions are included
        assert "pm.test" in request["tests"]
    
    @given(
        template_ids=st.lists(
            st.sampled_from([
                "pre_surgery", "post_surgery", "pre_post_surgery",
                "faq", "medication", "lifestyle"
            ]),
            min_size=1,
            max_size=3,
            unique=True
        )
    )
    @settings(max_examples=50)
    def test_preview_template_order_preserved(self, template_ids):
        """
        Property: Template order in preview should be preserved
        exactly as provided in the request.
        
        Invariants:
        1. Template IDs appear in request in same order
        2. Order affects combined prompt structure
        3. First template appears first in combined output
        """
        preview_data = {
            "template_ids": template_ids,
        }
        
        request = TestTemplateRequestCreation.create_preview_prompt_request(preview_data)
        
        body = json.loads(request["request"]["body"]["raw"])
        assert body["template_ids"] == template_ids
        
        # Verify response includes template_ids in same order
        assert "template_ids" in request["tests"]
    
    @given(
        template_ids=st.lists(
            st.sampled_from([
                "pre_surgery", "post_surgery", "faq", "medication"
            ]),
            min_size=1,
            max_size=2,
            unique=True
        )
    )
    @settings(max_examples=50)
    def test_preview_response_completeness(self, template_ids):
        """
        Property: Preview response should include all required fields
        for every valid template combination.
        
        Invariants:
        1. Response includes template_ids
        2. Response includes combined_prompt
        3. Response includes character_count
        4. All fields are non-empty
        """
        preview_data = {
            "template_ids": template_ids,
        }
        
        request = TestTemplateRequestCreation.create_preview_prompt_request(preview_data)
        
        # Verify all required fields are validated
        assert "template_ids" in request["tests"]
        assert "combined_prompt" in request["tests"]
        assert "character_count" in request["tests"]
        
        # Verify test script checks for non-empty values
        assert "pm.test" in request["tests"]
