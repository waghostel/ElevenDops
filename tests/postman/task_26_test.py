
"""
Tests for Task 26: Results Reporter Component
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open
from hypothesis import given, strategies as st
from tests.postman.results_reporter import ResultsReporter
from tests.postman.test_orchestrator import TestResult

# -----------------------------------------------------------------------------
# Strategies
# -----------------------------------------------------------------------------

@st.composite
def result_strategy(draw):
    """Generate a TestResult object."""
    status = draw(st.sampled_from(['passed', 'failed', 'error']))
    name = draw(st.text(min_size=1, max_size=20))
    duration = draw(st.floats(min_value=0.1, max_value=1000.0))
    error_msg = None
    if status != 'passed':
        error_msg = draw(st.text(min_size=1, max_size=50))
        
    return TestResult(
        name=name,
        status=status,
        duration_ms=duration,
        error_message=error_msg,
        assertions={'check_1': True} if status == 'passed' else {'check_1': False}
    )

# -----------------------------------------------------------------------------
# Unit Tests
# -----------------------------------------------------------------------------

def test_parse_results_empty():
    """Test parsing empty results."""
    reporter = ResultsReporter()
    metrics = reporter.parse_results([])
    assert metrics['total_tests'] == 0
    assert metrics['passed_tests'] == 0
    assert metrics['failed_tests'] == 0

def test_parse_results_mixed():
    """Test parsing mixed results."""
    reporter = ResultsReporter()
    results = [
        TestResult(name="pass", status="passed", duration_ms=100),
        TestResult(name="fail", status="failed", duration_ms=100, error_message="oops")
    ]
    metrics = reporter.parse_results(results)
    assert metrics['total_tests'] == 2
    assert metrics['passed_tests'] == 1
    assert metrics['failed_tests'] == 1
    assert metrics['success_rate'] == 50.0
    assert len(metrics['failures']) == 1

@patch("builtins.open", new_callable=mock_open)
def test_generate_summary_file_write(mock_file):
    """Test summary generation writes to file."""
    reporter = ResultsReporter(output_file="report.md")
    results = [TestResult(name="pass", status="passed", duration_ms=100)]
    report = reporter.generate_summary(results)
    
    assert "# Postman Test Run Summary" in report
    mock_file.assert_called_with("report.md", "w", encoding="utf-8")
    mock_file().write.assert_called_once()

@patch("tests.postman.results_reporter.PostmanConfigHelper")
def test_update_config_file_call(mock_helper):
    """Test config update call."""
    reporter = ResultsReporter()
    results = [TestResult(name="pass", status="passed", duration_ms=100)]
    reporter.update_config_file(results)
    
    mock_helper.update_config.assert_called_once()
    args = mock_helper.update_config.call_args[0][0]
    assert "last_run" in args
    assert args["last_run"]["passed"] == 1

# -----------------------------------------------------------------------------
# Property Tests
# -----------------------------------------------------------------------------

# Property 26.2: Test Result Summary Generation
@given(st.lists(result_strategy(), min_size=1))
def test_result_summary_generation_property(results):
    """Property 34: Test Result Summary Generation"""
    reporter = ResultsReporter()
    metrics = reporter.parse_results(results)
    
    # Check basic math
    assert metrics['total_tests'] == len(results)
    assert metrics['passed_tests'] + metrics['failed_tests'] == metrics['total_tests']
    
    passed_count = sum(1 for r in results if r.status == 'passed')
    assert metrics['passed_tests'] == passed_count
    
    # Check summary content
    summary = reporter.generate_summary(results)
    assert f"**Total Tests:** {metrics['total_tests']}" in summary
    assert f"**Passed:** {metrics['passed_tests']}" in summary

# Property 26.3: Test Failure Detail Reporting
@given(st.lists(result_strategy(), min_size=1))
def test_failure_detail_reporting_property(results):
    """Property 35: Test Failure Detail Reporting"""
    reporter = ResultsReporter()
    metrics = reporter.parse_results(results)
    
    failures = [r for r in results if r.status != 'passed']
    
    assert len(metrics['failures']) == len(failures)
    
    # Verify every failure message is preserved in order
    failure_errors = [f['error'] for f in metrics['failures']]
    expected_errors = [r.error_message for r in failures]
    assert failure_errors == expected_errors
        
    # Verify report contains failure sections
    if failures:
        report = reporter.generate_summary(results)
        assert "## Failures" in report
        for f in failures:
            # We can only assert names are present, exact count is hard with duplicates
            assert f.name in report
            if f.error_message:
                assert f.error_message in report

# Property 26.4: Configuration File Update
@given(st.lists(result_strategy(), min_size=1))
def test_configuration_file_update_property(results):
    """Property 36: Configuration File Update"""
    reporter = ResultsReporter()
    
    with patch("tests.postman.results_reporter.PostmanConfigHelper") as mock_helper:
        reporter.update_config_file(results)
        
        assert mock_helper.update_config.called
        call_arg = mock_helper.update_config.call_args[0][0]
        
        last_run = call_arg.get('last_run')
        assert last_run is not None
        assert last_run['total'] == len(results)
        assert last_run['passed'] == sum(1 for r in results if r.status == 'passed')
