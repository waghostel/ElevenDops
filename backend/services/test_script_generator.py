"""
Test Script Generator Component for Postman Testing

Generates JavaScript test scripts for Postman requests.
Supports status checks, schema validation, field checks, value assertions, and variable saving.

Requirements: 12.4
"""

import json
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TestScriptGenerator:
    """
    Generates JavaScript test scripts for Postman requests.
    
    Supports:
    - Status code assertions
    - Response schema validation
    - Field existence checks
    - Value assertions
    - Variable saving for chaining
    """
    
    @staticmethod
    def _to_js_literal(value: Any) -> str:
        """
        Convert Python value to safe JavaScript literal.
        
        Args:
            value: Python value
            
        Returns:
            String representation of JavaScript literal
        """
        # use json.dumps for safe serialization of basic types
        return json.dumps(value)

    @staticmethod
    def generate_status_check(expected_status: int) -> str:
        """
        Generate status code assertion.
        
        Args:
            expected_status: Expected HTTP status code
            
        Returns:
            JavaScript test script
        """
        script = f"""pm.test('Status code is {expected_status}', function () {{
    pm.response.to.have.status({expected_status});
}});
"""
        logger.debug(f"Generated status check for {expected_status}")
        return script
    
    @staticmethod
    def generate_schema_validation(required_fields: List[str]) -> str:
        """
        Generate response schema validation.
        
        Args:
            required_fields: List of required fields in response
            
        Returns:
            JavaScript test script
        """
        if not required_fields:
            return ""
        
        # Safe field access check
        field_checks = "\n    ".join([
            f"pm.expect(jsonData).to.have.property({TestScriptGenerator._to_js_literal(field)});"
            for field in required_fields
        ])
        
        script = f"""pm.test('Response has required fields', function () {{
    var jsonData = pm.response.json();
    {field_checks}
}});
"""
        logger.debug(f"Generated schema validation for {len(required_fields)} fields")
        return script
    
    @staticmethod
    def generate_field_check(field_path: str, field_type: str = "string") -> str:
        """
        Generate field existence and type check.
        
        Args:
            field_path: JSON path to field (e.g., "data.id")
            field_type: Expected field type (string, number, boolean, object, array)
            
        Returns:
            JavaScript test script
        """
        type_check_map = {
            "string": "typeof jsonData.{} === 'string'",
            "number": "typeof jsonData.{} === 'number'",
            "boolean": "typeof jsonData.{} === 'boolean'",
            "object": "typeof jsonData.{} === 'object'",
            "array": "Array.isArray(jsonData.{})",
        }
        
        type_check = type_check_map.get(field_type, "typeof jsonData.{} !== 'undefined'")
        type_check = type_check.format(field_path)
        
        script = f"""pm.test('Field {field_path} exists and is {field_type}', function () {{
    var jsonData = pm.response.json();
    pm.expect({type_check}).to.be.true;
}});
"""
        logger.debug(f"Generated field check for {field_path}")
        return script
    
    @staticmethod
    def generate_value_assertion(
        field_path: str,
        expected_value: Any,
        comparison: str = "equals",
    ) -> str:
        """
        Generate value comparison assertion.
        
        Args:
            field_path: JSON path to field
            expected_value: Expected value
            comparison: Comparison type (equals, contains, matches, greater_than, less_than)
            
        Returns:
            JavaScript test script
        """
        formatted_value = TestScriptGenerator._to_js_literal(expected_value)
        
        # Generate comparison
        if comparison == "matches":
            # For regex matches, use new RegExp() constructor with the string pattern
            comparison_code = f"pm.expect(jsonData.{field_path}).to.match(new RegExp({formatted_value}));"
        else:
            comparison_map = {
                "equals": f"pm.expect(jsonData.{field_path}).to.equal({formatted_value});",
                "contains": f"pm.expect(jsonData.{field_path}).to.include({formatted_value});",
                "greater_than": f"pm.expect(jsonData.{field_path}).to.be.above({formatted_value});",
                "less_than": f"pm.expect(jsonData.{field_path}).to.be.below({formatted_value});",
            }
            comparison_code = comparison_map.get(
                comparison,
                f"pm.expect(jsonData.{field_path}).to.equal({formatted_value});"
            )
        
        script = f"""pm.test('Field {field_path} {comparison} {formatted_value}', function () {{
    var jsonData = pm.response.json();
    {comparison_code}
}});
"""
        logger.debug(f"Generated value assertion for {field_path}")
        return script
    
    @staticmethod
    def generate_variable_save(
        var_name: str,
        json_path: str,
        scope: str = "collection",
    ) -> str:
        """
        Generate variable save script for chaining.
        
        Args:
            var_name: Variable name to save
            json_path: JSON path to extract value from
            scope: Variable scope (collection, environment, global)
            
        Returns:
            JavaScript test script
        """
        # Ensure var_name is safely quoted
        safe_var_name = TestScriptGenerator._to_js_literal(var_name)
        
        if scope == "collection":
            set_var = f"pm.collectionVariables.set({safe_var_name}, value);"
        elif scope == "environment":
            set_var = f"pm.environment.set({safe_var_name}, value);"
        elif scope == "global":
            set_var = f"pm.globals.set({safe_var_name}, value);"
        else:
            set_var = f"pm.collectionVariables.set({safe_var_name}, value);"
        
        script = f"""pm.test('Save {var_name} for chaining', function () {{
    var jsonData = pm.response.json();
    var value = jsonData.{json_path};
    pm.expect(value).to.not.be.undefined;
    {set_var}
}});
"""
        logger.debug(f"Generated variable save for {var_name}")
        return script
    
    @staticmethod
    def generate_response_time_check(max_ms: int = 1000) -> str:
        """
        Generate response time assertion.
        
        Args:
            max_ms: Maximum response time in milliseconds
            
        Returns:
            JavaScript test script
        """
        script = f"""pm.test('Response time is less than {max_ms}ms', function () {{
    pm.expect(pm.response.responseTime).to.be.below({max_ms});
}});
"""
        logger.debug(f"Generated response time check for {max_ms}ms")
        return script
    
    @staticmethod
    def generate_content_type_check(expected_type: str = "application/json") -> str:
        """
        Generate content type assertion.
        
        Args:
            expected_type: Expected content type
            
        Returns:
            JavaScript test script
        """
        safe_type = TestScriptGenerator._to_js_literal(expected_type)
        script = f"""pm.test('Content-Type is {expected_type}', function () {{
    pm.response.to.have.header('Content-Type');
    pm.expect(pm.response.headers.get('Content-Type')).to.include({safe_type});
}});
"""
        logger.debug(f"Generated content type check for {expected_type}")
        return script
    
    @staticmethod
    def generate_header_check(header_name: str, expected_value: Optional[str] = None) -> str:
        """
        Generate header existence check.
        
        Args:
            header_name: Header name to check
            expected_value: Optional expected header value
            
        Returns:
            JavaScript test script
        """
        safe_header_name = TestScriptGenerator._to_js_literal(header_name)
        if expected_value:
            safe_value = TestScriptGenerator._to_js_literal(expected_value)
            script = f"""pm.test('Header {header_name} equals {expected_value}', function () {{
    pm.response.to.have.header({safe_header_name});
    pm.expect(pm.response.headers.get({safe_header_name})).to.equal({safe_value});
}});
"""
        else:
            script = f"""pm.test('Header {header_name} exists', function () {{
    pm.response.to.have.header({safe_header_name});
}});
"""
        logger.debug(f"Generated header check for {header_name}")
        return script
    
    @staticmethod
    def generate_error_check(error_field: str = "error") -> str:
        """
        Generate error response check.
        
        Args:
            error_field: Field name containing error message
            
        Returns:
            JavaScript test script
        """
        safe_field = TestScriptGenerator._to_js_literal(error_field)
        script = f"""pm.test('Response contains error information', function () {{
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property({safe_field});
    pm.expect(jsonData.{error_field}).to.not.be.empty;
}});
"""
        logger.debug(f"Generated error check for {error_field}")
        return script
    
    @staticmethod
    def generate_array_length_check(
        array_path: str,
        min_length: int = 0,
        max_length: Optional[int] = None,
    ) -> str:
        """
        Generate array length assertion.
        
        Args:
            array_path: JSON path to array
            min_length: Minimum array length
            max_length: Maximum array length (optional)
            
        Returns:
            JavaScript test script
        """
        if max_length is not None:
            length_check = f"pm.expect(jsonData.{array_path}.length).to.be.within({min_length}, {max_length});"
            test_name = f"Array {array_path} length between {min_length} and {max_length}"
        else:
            length_check = f"pm.expect(jsonData.{array_path}.length).to.be.at.least({min_length});"
            test_name = f"Array {array_path} length at least {min_length}"
        
        script = f"""pm.test('{test_name}', function () {{
    var jsonData = pm.response.json();
    pm.expect(Array.isArray(jsonData.{array_path})).to.be.true;
    {length_check}
}});
"""
        logger.debug(f"Generated array length check for {array_path}")
        return script
    
    @staticmethod
    def combine_scripts(scripts: List[str]) -> str:
        """
        Combine multiple test scripts.
        
        Args:
            scripts: List of test scripts
            
        Returns:
            Combined JavaScript script
        """
        combined = "\n".join(scripts)
        logger.debug(f"Combined {len(scripts)} test scripts")
        return combined
    
    @staticmethod
    def validate_javascript(script: str) -> bool:
        """
        Basic validation that script looks like valid JavaScript.
        
        Args:
            script: JavaScript code to validate
            
        Returns:
            True if script appears valid
        """
        # Check for basic JavaScript patterns
        has_pm_test = "pm.test(" in script
        has_function = "function" in script
        has_closing_brace = "}" in script
        
        is_valid = has_pm_test and has_function and has_closing_brace
        
        if not is_valid:
            logger.warning("Generated script may not be valid JavaScript")
        
        return is_valid
    
    @staticmethod
    def generate_pre_request_script(
        variables: Dict[str, Any],
        timestamp: bool = True,
    ) -> str:
        """
        Generate pre-request script for setup.
        
        Args:
            variables: Variables to set
            timestamp: Whether to add timestamp
            
        Returns:
            JavaScript pre-request script
        """
        script_lines = []
        
        # Add timestamp if requested
        if timestamp:
            script_lines.append("pm.collectionVariables.set('timestamp', new Date().toISOString());")
        
        # Add variables
        for key, value in variables.items():
            safe_key = TestScriptGenerator._to_js_literal(key)
            safe_value = TestScriptGenerator._to_js_literal(value)
            script_lines.append(f"pm.collectionVariables.set({safe_key}, {safe_value});")
        
        script = "\n".join(script_lines)
        logger.debug(f"Generated pre-request script with {len(variables)} variables")
        return script


__all__ = ["TestScriptGenerator"]
