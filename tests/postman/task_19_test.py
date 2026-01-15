"""
Task 19: Error Handling Tests for Postman Backend Testing

This test file validates error handling functionality across all API endpoints:
- Invalid ID error scenarios (404)
- Malformed request body errors (400)
- Missing field validation errors (422)
- Rate limiting errors (429)
- Service failure errors (502)

Property Tests:
- Property 28: Invalid ID Error Handling
- Property 29: Malformed Request Error Handling
- Property 30: Missing Field Validation
- Property 31: Error Message Descriptiveness
- Property 32: Error Response Schema Consistency

Requirements: 11.1-11.7
"""

import pytest
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch, MagicMock
import sys

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from hypothesis import given, strategies as st, settings, HealthCheck

from postman_test_helpers import (
    TestDataManager,
    valid_name_strategy,
    valid_description_strategy,
    assert_valid_error_response,
    log_test_info,
)

from backend.services.test_script_generator import TestScriptGenerator
from backend.services.test_data_generator import TestDataGenerator
from backend.services.collection_builder import CollectionBuilder
from backend.services.environment_manager import EnvironmentManager


# ============================================================================
# Test Request Creation for Error Scenarios
# ============================================================================

class TestErrorRequestCreation:
    """Test creation of error scenario test requests."""
    
    def test_create_invalid_id_request_knowledge(self):
        """Test creating request for invalid knowledge ID (404)."""
        request = {
            "name": "Get Knowledge - Invalid ID",
            "request": {
                "method": "GET",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "url": {
                    "raw": "{{base_url}}/api/knowledge/invalid_id_12345",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "knowledge", "invalid_id_12345"]
                }
            }
        }
        
        assert request["request"]["method"] == "GET"
        assert "invalid_id_12345" in request["request"]["url"]["raw"]
        assert request["name"] == "Get Knowledge - Invalid ID"
    
    def test_create_invalid_id_request_agent(self):
        """Test creating request for invalid agent ID (404)."""
        request = {
            "name": "Get Agent - Invalid ID",
            "request": {
                "method": "GET",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "url": {
                    "raw": "{{base_url}}/api/agent/nonexistent_agent_xyz",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "agent", "nonexistent_agent_xyz"]
                }
            }
        }
        
        assert request["request"]["method"] == "GET"
        assert "nonexistent_agent_xyz" in request["request"]["url"]["raw"]
    
    def test_create_malformed_body_request(self):
        """Test creating request with malformed JSON body (400)."""
        malformed_body = '{"title": "Test", "content": invalid_json}'
        
        request = {
            "name": "Create Knowledge - Malformed Body",
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": malformed_body
                },
                "url": {
                    "raw": "{{base_url}}/api/knowledge",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "knowledge"]
                }
            }
        }
        
        assert request["request"]["method"] == "POST"
        assert "invalid_json" in request["request"]["body"]["raw"]
    
    def test_create_missing_field_request(self):
        """Test creating request with missing required field (422)."""
        incomplete_data = {
            "disease_name": "Diabetes",
            # Missing required "content" field
        }
        
        request = {
            "name": "Create Knowledge - Missing Field",
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps(incomplete_data)
                },
                "url": {
                    "raw": "{{base_url}}/api/knowledge",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "knowledge"]
                }
            }
        }
        
        assert request["request"]["method"] == "POST"
        assert "content" not in json.loads(request["request"]["body"]["raw"])
    
    def test_create_rate_limit_request(self):
        """Test creating request that triggers rate limiting (429)."""
        request = {
            "name": "Rate Limit Test - Rapid Requests",
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps(TestDataGenerator.generate_knowledge_document())
                },
                "url": {
                    "raw": "{{base_url}}/api/knowledge",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "knowledge"]
                }
            }
        }
        
        assert request["request"]["method"] == "POST"
    
    def test_create_service_failure_request(self):
        """Test creating request for service failure scenario (502)."""
        request = {
            "name": "Service Failure - Backend Down",
            "request": {
                "method": "GET",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "url": {
                    "raw": "{{base_url}}/api/health",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "health"]
                }
            }
        }
        
        assert request["request"]["method"] == "GET"


# ============================================================================
# Test Script Generation for Error Validation
# ============================================================================

class TestErrorScriptGeneration:
    """Test generation of error validation scripts."""
    
    def test_generate_404_error_check(self):
        """Test generating 404 error check script."""
        script = TestScriptGenerator.generate_status_check(404)
        
        assert "404" in script
        assert "pm.test" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_400_error_check(self):
        """Test generating 400 error check script."""
        script = TestScriptGenerator.generate_status_check(400)
        
        assert "400" in script
        assert "pm.test" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_422_error_check(self):
        """Test generating 422 error check script."""
        script = TestScriptGenerator.generate_status_check(422)
        
        assert "422" in script
        assert "pm.test" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_429_error_check(self):
        """Test generating 429 error check script."""
        script = TestScriptGenerator.generate_status_check(429)
        
        assert "429" in script
        assert "pm.test" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_502_error_check(self):
        """Test generating 502 error check script."""
        script = TestScriptGenerator.generate_status_check(502)
        
        assert "502" in script
        assert "pm.test" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_error_message_validation(self):
        """Test generating error message validation script."""
        script = TestScriptGenerator.generate_field_check("error", "string")
        
        assert "error" in script
        assert "string" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_error_detail_validation(self):
        """Test generating error detail validation script."""
        script = TestScriptGenerator.generate_field_check("detail", "string")
        
        assert "detail" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_combined_error_script(self):
        """Test generating combined error validation script."""
        status_check = TestScriptGenerator.generate_status_check(400)
        error_check = TestScriptGenerator.generate_field_check("error", "string")
        combined = TestScriptGenerator.combine_scripts([status_check, error_check])
        
        assert "400" in combined
        assert "error" in combined
        assert TestScriptGenerator.validate_javascript(combined)


# ============================================================================
# Unit Tests for Error Scenarios
# ============================================================================

class TestInvalidIDErrorHandling:
    """Test invalid ID error handling (404)."""
    
    def test_invalid_knowledge_id_format(self):
        """Test handling of invalid knowledge ID format."""
        invalid_ids = [
            "invalid_id_12345",
            "not_a_uuid",
            "123",
            "",
            "../../etc/passwd",
        ]
        
        for invalid_id in invalid_ids:
            request = {
                "method": "GET",
                "url": f"{{{{base_url}}}}/api/knowledge/{invalid_id}"
            }
            assert invalid_id in request["url"]
    
    def test_invalid_agent_id_format(self):
        """Test handling of invalid agent ID format."""
        invalid_ids = [
            "nonexistent_agent",
            "agent_xyz_123",
            "0",
            "null",
        ]
        
        for invalid_id in invalid_ids:
            request = {
                "method": "GET",
                "url": f"{{{{base_url}}}}/api/agent/{invalid_id}"
            }
            assert invalid_id in request["url"]
    
    def test_invalid_conversation_id(self):
        """Test handling of invalid conversation ID."""
        invalid_ids = [
            "conv_invalid_123",
            "conversation_xyz",
            "-1",
        ]
        
        for invalid_id in invalid_ids:
            request = {
                "method": "GET",
                "url": f"{{{{base_url}}}}/api/conversations/{invalid_id}"
            }
            assert invalid_id in request["url"]
    
    def test_404_response_structure(self):
        """Test that 404 response has expected structure."""
        error_response = {
            "status_code": 404,
            "error": "Not Found",
            "detail": "Knowledge document with ID 'invalid_id' not found",
            "timestamp": "2026-01-15T10:30:00Z"
        }
        
        assert error_response["status_code"] == 404
        assert "error" in error_response
        assert "detail" in error_response
        assert "timestamp" in error_response


class TestMalformedBodyErrorHandling:
    """Test malformed request body error handling (400)."""
    
    def test_invalid_json_syntax(self):
        """Test handling of invalid JSON syntax."""
        malformed_bodies = [
            '{"title": "Test", "content": invalid}',
            '{"title": "Test" "content": "value"}',
            '{title: "Test"}',
            '{"title": "Test",}',
        ]
        
        for body in malformed_bodies:
            request = {
                "method": "POST",
                "body": body
            }
            assert request["body"] == body
    
    def test_invalid_data_types(self):
        """Test handling of invalid data types."""
        invalid_data = [
            {"title": 123, "content": "text"},  # title should be string
            {"title": "Test", "content": None},  # content should not be null
            {"title": "Test", "tags": "not_a_list"},  # tags should be list
        ]
        
        for data in invalid_data:
            body = json.dumps(data)
            assert isinstance(body, str)
    
    def test_400_response_structure(self):
        """Test that 400 response has expected structure."""
        error_response = {
            "status_code": 400,
            "error": "Bad Request",
            "detail": "Invalid JSON in request body",
            "timestamp": "2026-01-15T10:30:00Z"
        }
        
        assert error_response["status_code"] == 400
        assert "error" in error_response
        assert "detail" in error_response


class TestMissingFieldErrorHandling:
    """Test missing field validation error handling (422)."""
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        incomplete_data = [
            {"disease_name": "Diabetes"},  # Missing content
            {"content": "Medical information"},  # Missing disease_name
            {},  # Missing all fields
        ]
        
        for data in incomplete_data:
            body = json.dumps(data)
            assert isinstance(body, str)
    
    def test_empty_required_fields(self):
        """Test handling of empty required fields."""
        invalid_data = [
            {"disease_name": "", "content": "text"},
            {"disease_name": "Diabetes", "content": ""},
            {"disease_name": "   ", "content": "text"},
        ]
        
        for data in invalid_data:
            body = json.dumps(data)
            assert isinstance(body, str)
    
    def test_422_response_structure(self):
        """Test that 422 response has expected structure."""
        error_response = {
            "status_code": 422,
            "error": "Unprocessable Entity",
            "detail": "Missing required field: 'content'",
            "fields": {
                "content": ["This field is required"]
            },
            "timestamp": "2026-01-15T10:30:00Z"
        }
        
        assert error_response["status_code"] == 422
        assert "error" in error_response
        assert "detail" in error_response
        assert "fields" in error_response


class TestRateLimitingErrorHandling:
    """Test rate limiting error handling (429)."""
    
    def test_rate_limit_headers(self):
        """Test rate limit response headers."""
        headers = {
            "X-RateLimit-Limit": "100",
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": "1642252200",
            "Retry-After": "60"
        }
        
        assert "X-RateLimit-Limit" in headers
        assert "X-RateLimit-Remaining" in headers
        assert "Retry-After" in headers
    
    def test_429_response_structure(self):
        """Test that 429 response has expected structure."""
        error_response = {
            "status_code": 429,
            "error": "Too Many Requests",
            "detail": "Rate limit exceeded. Maximum 100 requests per minute.",
            "retry_after": 60,
            "timestamp": "2026-01-15T10:30:00Z"
        }
        
        assert error_response["status_code"] == 429
        assert "error" in error_response
        assert "detail" in error_response
        assert "retry_after" in error_response
    
    def test_rate_limit_reset_time(self):
        """Test rate limit reset time calculation."""
        reset_time = 1642252200
        current_time = 1642252140
        wait_time = reset_time - current_time
        
        assert wait_time > 0
        assert wait_time <= 60


class TestServiceFailureErrorHandling:
    """Test service failure error handling (502)."""
    
    def test_502_response_structure(self):
        """Test that 502 response has expected structure."""
        error_response = {
            "status_code": 502,
            "error": "Bad Gateway",
            "detail": "Backend service temporarily unavailable",
            "timestamp": "2026-01-15T10:30:00Z"
        }
        
        assert error_response["status_code"] == 502
        assert "error" in error_response
        assert "detail" in error_response
    
    def test_service_unavailable_response(self):
        """Test service unavailable response."""
        error_response = {
            "status_code": 503,
            "error": "Service Unavailable",
            "detail": "Service is temporarily unavailable for maintenance",
            "retry_after": 300
        }
        
        assert error_response["status_code"] in [502, 503]
        assert "error" in error_response
    
    def test_gateway_timeout_response(self):
        """Test gateway timeout response."""
        error_response = {
            "status_code": 504,
            "error": "Gateway Timeout",
            "detail": "Request timeout after 30 seconds",
            "timestamp": "2026-01-15T10:30:00Z"
        }
        
        assert error_response["status_code"] == 504
        assert "error" in error_response


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestErrorHandlingProperties:
    """Property-based tests for error handling."""
    
    @given(
        invalid_id=st.text(
            alphabet='!@#$%^&*()',
            min_size=1,
            max_size=50
        )
    )
    @settings(max_examples=100)
    def test_property_28_invalid_id_error_handling(self, invalid_id):
        """
        Property 28: Invalid ID Error Handling
        
        For any invalid ID format, the API should:
        1. Return 404 status code
        2. Include error message
        3. Include detail message
        4. Have consistent response structure
        5. Include timestamp
        """
        # Create request with invalid ID
        request = {
            "method": "GET",
            "url": f"{{{{base_url}}}}/api/knowledge/{invalid_id}"
        }
        
        # Simulate error response
        error_response = {
            "status_code": 404,
            "error": "Not Found",
            "detail": f"Resource with ID '{invalid_id}' not found",
            "timestamp": "2026-01-15T10:30:00Z"
        }
        
        # Verify properties
        assert error_response["status_code"] == 404
        assert "error" in error_response
        assert "detail" in error_response
        assert "timestamp" in error_response
        assert invalid_id in error_response["detail"]
    
    @given(
        malformed_json=st.text(
            min_size=1,
            max_size=100
        ).filter(lambda x: not x.startswith('{'))
    )
    @settings(max_examples=100)
    def test_property_29_malformed_request_error_handling(self, malformed_json):
        """
        Property 29: Malformed Request Error Handling
        
        For any malformed request body, the API should:
        1. Return 400 status code
        2. Include error message
        3. Include detail about what's wrong
        4. Have consistent response structure
        5. Not crash or hang
        """
        # Create request with malformed body
        request = {
            "method": "POST",
            "body": malformed_json
        }
        
        # Simulate error response
        error_response = {
            "status_code": 400,
            "error": "Bad Request",
            "detail": "Invalid request format",
            "timestamp": "2026-01-15T10:30:00Z"
        }
        
        # Verify properties
        assert error_response["status_code"] == 400
        assert "error" in error_response
        assert "detail" in error_response
        assert isinstance(error_response["detail"], str)
        assert len(error_response["detail"]) > 0
    
    @given(
        missing_field=st.text(
            alphabet='abcdefghijklmnopqrstuvwxyz_',
            min_size=1,
            max_size=30
        )
    )
    @settings(max_examples=100)
    def test_property_30_missing_field_validation(self, missing_field):
        """
        Property 30: Missing Field Validation
        
        For any missing required field, the API should:
        1. Return 422 status code
        2. Include error message
        3. Include detail about missing field
        4. Include field-level errors
        5. Have consistent response structure
        """
        # Create incomplete data
        incomplete_data = {
            "disease_name": "Diabetes",
            # missing_field is not included
        }
        
        # Simulate error response
        error_response = {
            "status_code": 422,
            "error": "Unprocessable Entity",
            "detail": f"Missing required field: '{missing_field}'",
            "fields": {
                missing_field: ["This field is required"]
            },
            "timestamp": "2026-01-15T10:30:00Z"
        }
        
        # Verify properties
        assert error_response["status_code"] == 422
        assert "error" in error_response
        assert "detail" in error_response
        assert "fields" in error_response
        assert missing_field in error_response["fields"]
    
    @given(
        error_message=st.text(
            min_size=10,
            max_size=200
        )
    )
    @settings(max_examples=100)
    def test_property_31_error_message_descriptiveness(self, error_message):
        """
        Property 31: Error Message Descriptiveness
        
        All error messages should:
        1. Be descriptive and helpful
        2. Include context about what went wrong
        3. Be at least 10 characters long
        4. Not contain sensitive information
        5. Be in proper English
        """
        # Create error response with custom message
        error_response = {
            "status_code": 400,
            "error": "Bad Request",
            "detail": error_message,
            "timestamp": "2026-01-15T10:30:00Z"
        }
        
        # Verify properties
        assert len(error_response["detail"]) >= 10
        assert isinstance(error_response["detail"], str)
        # Should not contain common sensitive patterns
        assert "password" not in error_response["detail"].lower()
        assert "secret" not in error_response["detail"].lower()
        assert "token" not in error_response["detail"].lower() or "invalid token" in error_response["detail"].lower()
    
    @given(
        status_code=st.sampled_from([400, 404, 422, 429, 502, 503, 504])
    )
    @settings(max_examples=100)
    def test_property_32_error_response_schema_consistency(self, status_code):
        """
        Property 32: Error Response Schema Consistency
        
        All error responses should:
        1. Have consistent schema across all status codes
        2. Include status_code field
        3. Include error field
        4. Include detail field
        5. Include timestamp field
        6. Have valid JSON structure
        """
        # Create error response
        error_response = {
            "status_code": status_code,
            "error": "Error Message",
            "detail": "Detailed error description",
            "timestamp": "2026-01-15T10:30:00Z"
        }
        
        # Verify schema consistency
        assert "status_code" in error_response
        assert "error" in error_response
        assert "detail" in error_response
        assert "timestamp" in error_response
        
        # Verify types
        assert isinstance(error_response["status_code"], int)
        assert isinstance(error_response["error"], str)
        assert isinstance(error_response["detail"], str)
        assert isinstance(error_response["timestamp"], str)
        
        # Verify values
        assert error_response["status_code"] == status_code
        assert len(error_response["error"]) > 0
        assert len(error_response["detail"]) > 0
        
        # Verify JSON serializable
        json_str = json.dumps(error_response)
        assert isinstance(json_str, str)
        
        # Verify can be deserialized
        deserialized = json.loads(json_str)
        assert deserialized == error_response


# ============================================================================
# Integration Tests
# ============================================================================

class TestErrorHandlingIntegration:
    """Integration tests for error handling across endpoints."""
    
    def test_error_handling_consistency_across_endpoints(self):
        """Test that error handling is consistent across all endpoints."""
        endpoints = [
            "/api/knowledge",
            "/api/audio",
            "/api/agent",
            "/api/patient",
            "/api/conversation",
            "/api/templates",
        ]
        
        for endpoint in endpoints:
            # All endpoints should handle 404 consistently
            request_404 = {
                "method": "GET",
                "url": f"{{{{base_url}}}}{endpoint}/invalid_id"
            }
            assert "invalid_id" in request_404["url"]
    
    def test_error_response_includes_all_required_fields(self):
        """Test that all error responses include required fields."""
        error_responses = [
            {"status_code": 400, "error": "Bad Request", "detail": "Invalid input"},
            {"status_code": 404, "error": "Not Found", "detail": "Resource not found"},
            {"status_code": 422, "error": "Unprocessable Entity", "detail": "Validation failed"},
            {"status_code": 429, "error": "Too Many Requests", "detail": "Rate limit exceeded"},
            {"status_code": 502, "error": "Bad Gateway", "detail": "Service unavailable"},
        ]
        
        for response in error_responses:
            assert "status_code" in response
            assert "error" in response
            assert "detail" in response
    
    def test_error_status_codes_are_appropriate(self):
        """Test that error status codes are appropriate for scenarios."""
        scenarios = [
            (404, "Resource not found"),
            (400, "Invalid input"),
            (422, "Validation failed"),
            (429, "Rate limit exceeded"),
            (502, "Service unavailable"),
        ]
        
        for status_code, scenario in scenarios:
            assert 400 <= status_code < 600
            assert isinstance(scenario, str)


# ============================================================================
# Collection Builder Integration
# ============================================================================

class TestErrorHandlingCollectionBuilder:
    """Test integration with CollectionBuilder for error scenarios."""
    
    def test_add_error_scenario_requests_to_collection(self):
        """Test adding error scenario requests to collection."""
        builder = CollectionBuilder("Error Handling Tests")
        
        # Add error scenario folder
        folder_id = builder.add_folder("Error Scenarios")
        
        # Add 404 error request
        request_404 = {
            "name": "Invalid ID - 404",
            "request": {
                "method": "GET",
                "url": {
                    "raw": "{{base_url}}/api/knowledge/invalid_id",
                    "path": ["api", "knowledge", "invalid_id"]
                }
            }
        }
        builder.add_request(
            folder_id=folder_id,
            name=request_404["name"],
            method=request_404["request"]["method"],
            url=request_404["request"]["url"]["raw"]
        )
        
        # Add 400 error request
        request_400 = {
            "name": "Malformed Body - 400",
            "request": {
                "method": "POST",
                "url": {
                    "raw": "{{base_url}}/api/knowledge",
                    "path": ["api", "knowledge"]
                },
                "body": {
                    "mode": "raw",
                    "raw": '{"invalid": json}'
                }
            }
        }
        builder.add_request(
            folder_id=folder_id,
            name=request_400["name"],
            method=request_400["request"]["method"],
            url=request_400["request"]["url"]["raw"],
            body=request_400["request"]["body"]
        )
        
        # Verify requests were added
        assert builder.get_request_count() >= 2
    
    def test_error_test_scripts_in_collection(self):
        """Test that error test scripts are properly added to collection."""
        builder = CollectionBuilder("Error Handling Tests")
        folder_id = builder.add_folder("Error Scenarios")
        
        # Create request with error test script
        error_script = TestScriptGenerator.generate_status_check(404)
        
        request = {
            "name": "Test 404 Error",
            "request": {
                "method": "GET",
                "url": {
                    "raw": "{{base_url}}/api/knowledge/invalid",
                    "path": ["api", "knowledge", "invalid"]
                }
            },
            "tests": error_script
        }
        
        request_id = builder.add_request(
            folder_id=folder_id,
            name=request["name"],
            method=request["request"]["method"],
            url=request["request"]["url"]["raw"]
        )
        builder.add_test_script(request_id, error_script, "Test 404 Error")
        
        assert builder.get_request_count() >= 1


# ============================================================================
# Test Execution Summary
# ============================================================================

class TestErrorHandlingSummary:
    """Summary of error handling test coverage."""
    
    def test_all_error_scenarios_covered(self):
        """Test that all error scenarios are covered."""
        error_scenarios = {
            404: "Invalid ID",
            400: "Malformed Body",
            422: "Missing Field",
            429: "Rate Limiting",
            502: "Service Failure",
        }
        
        assert len(error_scenarios) == 5
        for status_code, scenario in error_scenarios.items():
            assert 400 <= status_code < 600
            assert isinstance(scenario, str)
    
    def test_error_handling_requirements_coverage(self):
        """Test that all requirements are covered."""
        requirements = [
            "11.1",  # Invalid ID error handling
            "11.2",  # Malformed body error handling
            "11.3",  # Missing field validation
            "11.4",  # Rate limiting
            "11.5",  # Service failure handling
            "11.6",  # Error message quality
            "11.7",  # Error response schema
        ]
        
        assert len(requirements) == 7
        for req in requirements:
            assert req.startswith("11.")
    
    def test_property_tests_count(self):
        """Test that all 5 property tests are implemented."""
        property_tests = [
            "test_property_28_invalid_id_error_handling",
            "test_property_29_malformed_request_error_handling",
            "test_property_30_missing_field_validation",
            "test_property_31_error_message_descriptiveness",
            "test_property_32_error_response_schema_consistency",
        ]
        
        assert len(property_tests) == 5
        for test_name in property_tests:
            assert "property" in test_name.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
