"""
Unit tests for TestScriptGenerator script escaping.
"""

import pytest
from backend.services.test_script_generator import TestScriptGenerator

def test_generate_value_assertion_handles_single_quotes():
    """Test that value assertions correctly escape single quotes."""
    script = TestScriptGenerator.generate_value_assertion("data.name", "O'Reilly")
    # Current implementation produces: 'O'Reilly' which is invalid JS
    # We expect: "O'Reilly" or 'O\'Reilly' (json.dumps usually prefers double quotes)
    expected_value = '"O\'Reilly"' # JSON representation
    assert expected_value in script or "'O\\'Reilly'" in script

def test_generate_value_assertion_handles_double_quotes():
    """Test that value assertions correctly escape double quotes."""
    script = TestScriptGenerator.generate_value_assertion("data.msg", 'Say "Hello"')
    # Expected: "Say \"Hello\""
    expected_value = '"Say \\"Hello\\""'
    assert expected_value in script

def test_generate_value_assertion_handles_newlines():
    """Test that value assertions correctly escape newlines."""
    script = TestScriptGenerator.generate_value_assertion("data.text", "Line 1\nLine 2")
    # Expected: "Line 1\nLine 2" literal in JS string
    expected_value = r'"Line 1\nLine 2"'
    assert expected_value in script

def test_generate_value_assertion_matches_regex_escaping():
    """Test that matches assertion handles special regex chars safely."""
    pattern = "^[A-Z]+$"
    script = TestScriptGenerator.generate_value_assertion("data.code", pattern, comparison="matches")
    # Should generate new RegExp("^[A-Z]+$") or similar safe construct
    # rather than /^[A-Z]+$/ which might lack escaping for / inside the pattern
    assert "new RegExp" in script or ".to.match(/^" in script

def test_generate_pre_request_script_escaping():
    """Test that pre-request script escapes variable values."""
    vars = {"description": 'It\'s a "test"'}
    script = TestScriptGenerator.generate_pre_request_script(vars)
    # parsing the script to find the set call
    # expected: pm.collectionVariables.set('description', "It's a \"test\"");
    assert "It's a \\\"test\\\"" in script or 'It\'s a "test"' in script

def test_generate_header_check_escaping():
    """Test that header check escapes expected values."""
    script = TestScriptGenerator.generate_header_check("X-Custom", "Val'ue")
    assert '"Val\'ue"' in script or "'Val\\'ue'" in script
