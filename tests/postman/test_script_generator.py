"""
Task 7: Test Script Generator Component Tests

This test file validates test script generation functionality:
- TestScriptGenerator class implementation
- JavaScript test script generation
- Unit tests for all generator methods
- Validation of generated JavaScript
"""

import pytest
import re
from pathlib import Path
from typing import List

from postman_test_helpers import TestDataManager

# Import backend modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.test_script_generator import TestScriptGenerator


class TestStatusCheckGeneration:
    """Test status code check generation."""
    
    def test_generate_status_check_200(self):
        """Test generating 200 status check."""
        script = TestScriptGenerator.generate_status_check(200)
        
        assert "pm.test" in script
        assert "200" in script
        assert "pm.response.to.have.status" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_status_check_201(self):
        """Test generating 201 status check."""
        script = TestScriptGenerator.generate_status_check(201)
        
        assert "201" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_status_check_404(self):
        """Test generating 404 status check."""
        script = TestScriptGenerator.generate_status_check(404)
        
        assert "404" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_status_check_500(self):
        """Test generating 500 status check."""
        script = TestScriptGenerator.generate_status_check(500)
        
        assert "500" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_status_check_is_valid_javascript(self):
        """Test that generated status check is valid JavaScript."""
        script = TestScriptGenerator.generate_status_check(200)
        
        # Check for JavaScript patterns
        assert "function" in script
        assert "{" in script
        assert "}" in script
        assert "pm.test(" in script


class TestSchemaValidationGeneration:
    """Test schema validation generation."""
    
    def test_generate_schema_validation_single_field(self):
        """Test generating schema validation for single field."""
        script = TestScriptGenerator.generate_schema_validation(["id"])
        
        assert "pm.test" in script
        assert "id" in script
        assert "have.property" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_schema_validation_multiple_fields(self):
        """Test generating schema validation for multiple fields."""
        fields = ["id", "name", "email"]
        script = TestScriptGenerator.generate_schema_validation(fields)
        
        for field in fields:
            assert field in script
        
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_schema_validation_empty_fields(self):
        """Test generating schema validation with empty fields."""
        script = TestScriptGenerator.generate_schema_validation([])
        
        assert script == ""
    
    def test_schema_validation_structure(self):
        """Test schema validation structure."""
        script = TestScriptGenerator.generate_schema_validation(["id", "name"])
        
        assert "jsonData" in script
        assert "pm.expect" in script
        assert "to.have.property" in script


class TestFieldCheckGeneration:
    """Test field check generation."""
    
    def test_generate_field_check_string(self):
        """Test generating field check for string type."""
        script = TestScriptGenerator.generate_field_check("data.name", "string")
        
        assert "data.name" in script
        assert "string" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_field_check_number(self):
        """Test generating field check for number type."""
        script = TestScriptGenerator.generate_field_check("data.count", "number")
        
        assert "data.count" in script
        assert "number" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_field_check_boolean(self):
        """Test generating field check for boolean type."""
        script = TestScriptGenerator.generate_field_check("data.active", "boolean")
        
        assert "data.active" in script
        assert "boolean" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_field_check_array(self):
        """Test generating field check for array type."""
        script = TestScriptGenerator.generate_field_check("data.items", "array")
        
        assert "data.items" in script
        assert "Array.isArray" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_field_check_object(self):
        """Test generating field check for object type."""
        script = TestScriptGenerator.generate_field_check("data.metadata", "object")
        
        assert "data.metadata" in script
        assert "object" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_field_check_invalid_type(self):
        """Test generating field check with invalid type."""
        script = TestScriptGenerator.generate_field_check("data.field", "invalid")
        
        # Should still generate valid script with default check
        assert TestScriptGenerator.validate_javascript(script)


class TestValueAssertionGeneration:
    """Test value assertion generation."""
    
    def test_generate_value_assertion_equals_string(self):
        """Test generating value assertion for string equality."""
        script = TestScriptGenerator.generate_value_assertion(
            "data.status",
            "active",
            "equals"
        )
        
        assert "data.status" in script
        assert "active" in script
        assert "to.equal" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_value_assertion_equals_number(self):
        """Test generating value assertion for number equality."""
        script = TestScriptGenerator.generate_value_assertion(
            "data.count",
            42,
            "equals"
        )
        
        assert "data.count" in script
        assert "42" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_value_assertion_equals_boolean(self):
        """Test generating value assertion for boolean equality."""
        script = TestScriptGenerator.generate_value_assertion(
            "data.active",
            True,
            "equals"
        )
        
        assert "data.active" in script
        assert "true" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_value_assertion_contains(self):
        """Test generating contains assertion."""
        script = TestScriptGenerator.generate_value_assertion(
            "data.tags",
            "important",
            "contains"
        )
        
        assert "data.tags" in script
        assert "important" in script
        assert "to.include" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_value_assertion_matches(self):
        """Test generating regex match assertion."""
        script = TestScriptGenerator.generate_value_assertion(
            "data.email",
            ".*@example.com",
            "matches"
        )
        
        assert "data.email" in script
        assert "to.match" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_value_assertion_greater_than(self):
        """Test generating greater than assertion."""
        script = TestScriptGenerator.generate_value_assertion(
            "data.score",
            100,
            "greater_than"
        )
        
        assert "data.score" in script
        assert "100" in script
        assert "to.be.above" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_value_assertion_less_than(self):
        """Test generating less than assertion."""
        script = TestScriptGenerator.generate_value_assertion(
            "data.time",
            1000,
            "less_than"
        )
        
        assert "data.time" in script
        assert "1000" in script
        assert "to.be.below" in script
        assert TestScriptGenerator.validate_javascript(script)


class TestVariableSaveGeneration:
    """Test variable save generation."""
    
    def test_generate_variable_save_collection_scope(self):
        """Test generating variable save for collection scope."""
        script = TestScriptGenerator.generate_variable_save(
            "resource_id",
            "data.id",
            "collection"
        )
        
        assert "resource_id" in script
        assert "data.id" in script
        assert "pm.collectionVariables.set" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_variable_save_environment_scope(self):
        """Test generating variable save for environment scope."""
        script = TestScriptGenerator.generate_variable_save(
            "token",
            "data.token",
            "environment"
        )
        
        assert "token" in script
        assert "pm.environment.set" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_variable_save_global_scope(self):
        """Test generating variable save for global scope."""
        script = TestScriptGenerator.generate_variable_save(
            "session_id",
            "data.session_id",
            "global"
        )
        
        assert "session_id" in script
        assert "pm.globals.set" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_variable_save_nested_path(self):
        """Test generating variable save with nested JSON path."""
        script = TestScriptGenerator.generate_variable_save(
            "user_id",
            "data.user.id"
        )
        
        assert "user_id" in script
        assert "data.user.id" in script
        assert TestScriptGenerator.validate_javascript(script)


class TestResponseTimeCheckGeneration:
    """Test response time check generation."""
    
    def test_generate_response_time_check_default(self):
        """Test generating response time check with default timeout."""
        script = TestScriptGenerator.generate_response_time_check()
        
        assert "1000" in script
        assert "pm.response.responseTime" in script
        assert "to.be.below" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_response_time_check_custom(self):
        """Test generating response time check with custom timeout."""
        script = TestScriptGenerator.generate_response_time_check(500)
        
        assert "500" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_response_time_check_large_timeout(self):
        """Test generating response time check with large timeout."""
        script = TestScriptGenerator.generate_response_time_check(5000)
        
        assert "5000" in script
        assert TestScriptGenerator.validate_javascript(script)


class TestContentTypeCheckGeneration:
    """Test content type check generation."""
    
    def test_generate_content_type_check_json(self):
        """Test generating content type check for JSON."""
        script = TestScriptGenerator.generate_content_type_check("application/json")
        
        assert "application/json" in script
        assert "Content-Type" in script
        assert "pm.response.to.have.header" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_content_type_check_xml(self):
        """Test generating content type check for XML."""
        script = TestScriptGenerator.generate_content_type_check("application/xml")
        
        assert "application/xml" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_content_type_check_html(self):
        """Test generating content type check for HTML."""
        script = TestScriptGenerator.generate_content_type_check("text/html")
        
        assert "text/html" in script
        assert TestScriptGenerator.validate_javascript(script)


class TestHeaderCheckGeneration:
    """Test header check generation."""
    
    def test_generate_header_check_existence(self):
        """Test generating header existence check."""
        script = TestScriptGenerator.generate_header_check("Authorization")
        
        assert "Authorization" in script
        assert "pm.response.to.have.header" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_header_check_with_value(self):
        """Test generating header value check."""
        script = TestScriptGenerator.generate_header_check(
            "X-Custom-Header",
            "custom-value"
        )
        
        assert "X-Custom-Header" in script
        assert "custom-value" in script
        assert "to.equal" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_header_check_multiple_headers(self):
        """Test generating checks for multiple headers."""
        headers = ["Authorization", "Content-Type", "X-Request-ID"]
        scripts = [TestScriptGenerator.generate_header_check(h) for h in headers]
        
        for script in scripts:
            assert TestScriptGenerator.validate_javascript(script)


class TestErrorCheckGeneration:
    """Test error check generation."""
    
    def test_generate_error_check_default(self):
        """Test generating error check with default field."""
        script = TestScriptGenerator.generate_error_check()
        
        assert "error" in script
        assert "pm.expect" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_error_check_custom_field(self):
        """Test generating error check with custom field."""
        script = TestScriptGenerator.generate_error_check("error_message")
        
        assert "error_message" in script
        assert TestScriptGenerator.validate_javascript(script)


class TestArrayLengthCheckGeneration:
    """Test array length check generation."""
    
    def test_generate_array_length_check_minimum(self):
        """Test generating array length check with minimum."""
        script = TestScriptGenerator.generate_array_length_check("data.items", 1)
        
        assert "data.items" in script
        assert "1" in script
        assert "at.least" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_array_length_check_range(self):
        """Test generating array length check with range."""
        script = TestScriptGenerator.generate_array_length_check(
            "data.items",
            1,
            10
        )
        
        assert "data.items" in script
        assert "1" in script
        assert "10" in script
        assert "within" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_array_length_check_zero_minimum(self):
        """Test generating array length check with zero minimum."""
        script = TestScriptGenerator.generate_array_length_check("data.items", 0)
        
        assert "data.items" in script
        assert TestScriptGenerator.validate_javascript(script)


class TestScriptCombination:
    """Test combining multiple scripts."""
    
    def test_combine_scripts(self):
        """Test combining multiple test scripts."""
        script1 = TestScriptGenerator.generate_status_check(200)
        script2 = TestScriptGenerator.generate_field_check("data.id", "string")
        
        combined = TestScriptGenerator.combine_scripts([script1, script2])
        
        assert script1 in combined
        assert script2 in combined
        assert TestScriptGenerator.validate_javascript(combined)
    
    def test_combine_multiple_scripts(self):
        """Test combining many scripts."""
        scripts = [
            TestScriptGenerator.generate_status_check(200),
            TestScriptGenerator.generate_schema_validation(["id", "name"]),
            TestScriptGenerator.generate_response_time_check(1000),
            TestScriptGenerator.generate_content_type_check("application/json"),
        ]
        
        combined = TestScriptGenerator.combine_scripts(scripts)
        
        for script in scripts:
            assert script in combined
    
    def test_combine_empty_scripts(self):
        """Test combining empty script list."""
        combined = TestScriptGenerator.combine_scripts([])
        
        assert combined == ""


class TestJavaScriptValidation:
    """Test JavaScript validation."""
    
    def test_validate_valid_script(self):
        """Test validating valid script."""
        script = TestScriptGenerator.generate_status_check(200)
        
        assert TestScriptGenerator.validate_javascript(script) is True
    
    def test_validate_invalid_script_no_pm_test(self):
        """Test validating script without pm.test."""
        script = "var x = 5;"
        
        assert TestScriptGenerator.validate_javascript(script) is False
    
    def test_validate_invalid_script_no_function(self):
        """Test validating script without function."""
        script = "pm.test('test', 5);"
        
        assert TestScriptGenerator.validate_javascript(script) is False
    
    def test_validate_invalid_script_no_braces(self):
        """Test validating script without braces."""
        script = "pm.test('test', function () pm.response.to.have.status(200));"
        
        assert TestScriptGenerator.validate_javascript(script) is False


class TestPreRequestScriptGeneration:
    """Test pre-request script generation."""
    
    def test_generate_pre_request_script_with_timestamp(self):
        """Test generating pre-request script with timestamp."""
        script = TestScriptGenerator.generate_pre_request_script(
            {"var1": "value1"},
            timestamp=True
        )
        
        assert "timestamp" in script
        assert "var1" in script
        assert "value1" in script
    
    def test_generate_pre_request_script_without_timestamp(self):
        """Test generating pre-request script without timestamp."""
        script = TestScriptGenerator.generate_pre_request_script(
            {"var1": "value1"},
            timestamp=False
        )
        
        assert "timestamp" not in script
        assert "var1" in script
    
    def test_generate_pre_request_script_multiple_variables(self):
        """Test generating pre-request script with multiple variables."""
        variables = {
            "var1": "value1",
            "var2": "value2",
            "var3": "value3",
        }
        
        script = TestScriptGenerator.generate_pre_request_script(variables)
        
        for key, value in variables.items():
            assert key in script
            assert value in script
    
    def test_generate_pre_request_script_complex_values(self):
        """Test generating pre-request script with complex values."""
        variables = {
            "string_var": "test",
            "number_var": 42,
            "bool_var": True,
            "list_var": [1, 2, 3],
        }
        
        script = TestScriptGenerator.generate_pre_request_script(variables)
        
        assert "string_var" in script
        assert "number_var" in script
        assert "bool_var" in script
        assert "list_var" in script


class TestScriptGeneratorIntegration:
    """Integration tests for script generator."""
    
    def test_generate_complete_test_suite(self):
        """Test generating a complete test suite."""
        scripts = [
            TestScriptGenerator.generate_status_check(200),
            TestScriptGenerator.generate_schema_validation(["id", "name", "email"]),
            TestScriptGenerator.generate_field_check("data.id", "string"),
            TestScriptGenerator.generate_value_assertion("data.status", "active"),
            TestScriptGenerator.generate_response_time_check(1000),
            TestScriptGenerator.generate_content_type_check("application/json"),
            TestScriptGenerator.generate_variable_save("resource_id", "data.id"),
        ]
        
        combined = TestScriptGenerator.combine_scripts(scripts)
        
        assert TestScriptGenerator.validate_javascript(combined)
        assert len(combined) > 0
    
    def test_generate_error_handling_tests(self):
        """Test generating error handling tests."""
        scripts = [
            TestScriptGenerator.generate_status_check(404),
            TestScriptGenerator.generate_error_check("error"),
            TestScriptGenerator.generate_field_check("error", "string"),
        ]
        
        combined = TestScriptGenerator.combine_scripts(scripts)
        
        assert TestScriptGenerator.validate_javascript(combined)
    
    def test_generate_workflow_tests(self):
        """Test generating workflow tests."""
        scripts = [
            TestScriptGenerator.generate_status_check(201),
            TestScriptGenerator.generate_schema_validation(["id"]),
            TestScriptGenerator.generate_variable_save("created_id", "data.id"),
        ]
        
        combined = TestScriptGenerator.combine_scripts(scripts)
        
        assert TestScriptGenerator.validate_javascript(combined)


@pytest.mark.postman
class TestScriptGeneratorEdgeCases:
    """Test edge cases in script generation."""
    
    def test_generate_script_with_special_characters(self):
        """Test generating script with special characters in values."""
        script = TestScriptGenerator.generate_value_assertion(
            "data.message",
            "Hello 'World' \"Test\"",
            "equals"
        )
        
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_script_with_unicode(self):
        """Test generating script with unicode characters."""
        script = TestScriptGenerator.generate_value_assertion(
            "data.name",
            "José García",
            "equals"
        )
        
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_script_with_very_long_path(self):
        """Test generating script with very long JSON path."""
        long_path = "data.level1.level2.level3.level4.level5.value"
        script = TestScriptGenerator.generate_field_check(long_path, "string")
        
        assert long_path in script
        assert TestScriptGenerator.validate_javascript(script)
