"""
Unit tests for NewmanRunner component.

Tests the Newman CLI wrapper functionality including:
- Installation detection
- Collection execution via subprocess
- JSON report parsing
"""

import json
import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from tests.postman.newman_runner import NewmanRunner, NewmanResult, parse_newman_report_file
from tests.postman.test_orchestrator import TestResult


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def newman_runner() -> NewmanRunner:
    """Provide a fresh NewmanRunner instance."""
    return NewmanRunner(timeout=30)


@pytest.fixture
def sample_newman_report() -> Dict[str, Any]:
    """Sample Newman JSON report structure."""
    return {
        "run": {
            "stats": {
                "requests": {"total": 3, "failed": 1},
                "assertions": {"total": 5, "failed": 1},
            },
            "timings": {
                "started": 1000,
                "completed": 2500,
            },
            "executions": [
                {
                    "item": {"name": "Health Check"},
                    "response": {"code": 200, "responseTime": 45},
                    "assertions": [
                        {"assertion": "Status code is 200", "error": None},
                        {"assertion": "Response time < 500ms", "error": None},
                    ],
                },
                {
                    "item": {"name": "Create Document"},
                    "response": {"code": 201, "responseTime": 120},
                    "assertions": [
                        {"assertion": "Status code is 201", "error": None},
                    ],
                },
                {
                    "item": {"name": "Get Document"},
                    "response": {"code": 404, "responseTime": 30},
                    "assertions": [
                        {"assertion": "Status code is 200", "error": {"message": "expected 200 but got 404"}},
                        {"assertion": "Has document ID", "error": None},
                    ],
                },
            ],
        }
    }


@pytest.fixture
def temp_report_file(sample_newman_report) -> str:
    """Create a temporary Newman report file."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        json.dump(sample_newman_report, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except OSError:
        pass


@pytest.fixture
def temp_collection_file() -> str:
    """Create a minimal valid Postman collection file."""
    collection = {
        "info": {
            "name": "Test Collection",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": [
            {
                "name": "Health Check",
                "request": {
                    "method": "GET",
                    "url": "http://localhost:8000/api/health",
                },
            }
        ],
    }
    
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        json.dump(collection, f)
        temp_path = f.name
    
    yield temp_path
    
    try:
        os.unlink(temp_path)
    except OSError:
        pass


# =============================================================================
# Tests: is_newman_installed
# =============================================================================

class TestNewmanInstallation:
    """Tests for Newman installation detection."""

    def test_is_newman_installed_returns_bool(self, newman_runner: NewmanRunner):
        """is_newman_installed should return a boolean."""
        result = newman_runner.is_newman_installed()
        assert isinstance(result, bool)

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_is_newman_installed_true_when_available(
        self, mock_run, mock_which, newman_runner: NewmanRunner
    ):
        """Returns True when newman is in PATH and responds to --version."""
        mock_which.return_value = "/usr/local/bin/newman"
        mock_run.return_value = MagicMock(returncode=0, stdout="6.0.0")
        
        assert newman_runner.is_newman_installed() is True
        mock_which.assert_called_once_with("newman")

    @patch("shutil.which")
    def test_is_newman_installed_false_when_not_in_path(
        self, mock_which, newman_runner: NewmanRunner
    ):
        """Returns False when newman is not in PATH."""
        mock_which.return_value = None
        
        assert newman_runner.is_newman_installed() is False


# =============================================================================
# Tests: JSON Report Parsing
# =============================================================================

class TestNewmanReportParsing:
    """Tests for Newman JSON report parsing."""

    def test_parse_newman_json_report_success(
        self, newman_runner: NewmanRunner, temp_report_file: str
    ):
        """Successfully parses a valid Newman JSON report."""
        result = newman_runner._parse_newman_json_report(temp_report_file)
        
        assert isinstance(result, NewmanResult)
        assert result.total_requests == 3
        assert result.failed_requests == 1
        assert result.total_assertions == 5
        assert result.failed_assertions == 1
        assert result.duration_ms == 1500  # 2500 - 1000
        assert len(result.test_results) == 3

    def test_parse_newman_json_report_extracts_test_results(
        self, newman_runner: NewmanRunner, temp_report_file: str
    ):
        """Correctly extracts individual test results from report."""
        result = newman_runner._parse_newman_json_report(temp_report_file)
        
        # First result: Health Check (passed)
        health_result = result.test_results[0]
        assert health_result.name == "Health Check"
        assert health_result.status == "passed"
        assert health_result.duration_ms == 45
        assert health_result.error_message is None
        
        # Third result: Get Document (failed)
        get_result = result.test_results[2]
        assert get_result.name == "Get Document"
        assert get_result.status == "failed"
        assert get_result.error_message == "expected 200 but got 404"

    def test_parse_newman_json_report_handles_missing_file(
        self, newman_runner: NewmanRunner
    ):
        """Returns error result for non-existent file."""
        result = newman_runner._parse_newman_json_report("/nonexistent/path.json")
        
        assert result.success is False
        assert "path.json" in (result.error_message or "")

    def test_parse_newman_report_file_standalone_function(
        self, temp_report_file: str
    ):
        """Standalone parse function returns list of TestResult."""
        results = parse_newman_report_file(temp_report_file)
        
        assert isinstance(results, list)
        assert len(results) == 3
        assert all(isinstance(r, TestResult) for r in results)


# =============================================================================
# Tests: run_collection
# =============================================================================

class TestRunCollection:
    """Tests for collection execution."""

    def test_run_collection_missing_newman_returns_error(
        self, newman_runner: NewmanRunner
    ):
        """Returns error when Newman is not installed."""
        with patch.object(newman_runner, "is_newman_installed", return_value=False):
            result = newman_runner.run_collection("/path/to/collection.json")
        
        assert result.success is False
        assert "not installed" in (result.error_message or "").lower()

    def test_run_collection_missing_file_returns_error(
        self, newman_runner: NewmanRunner
    ):
        """Returns error when collection file doesn't exist."""
        with patch.object(newman_runner, "is_newman_installed", return_value=True):
            result = newman_runner.run_collection("/nonexistent/collection.json")
        
        assert result.success is False
        assert "not found" in (result.error_message or "").lower()

    @patch("subprocess.run")
    def test_run_collection_subprocess_timeout(
        self, mock_run, newman_runner: NewmanRunner, temp_collection_file: str
    ):
        """Handles subprocess timeout gracefully."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="newman", timeout=30)
        
        with patch.object(newman_runner, "is_newman_installed", return_value=True):
            result = newman_runner.run_collection(temp_collection_file)
        
        assert result.success is False
        assert "timed out" in (result.error_message or "").lower()


# =============================================================================
# Tests: NewmanResult
# =============================================================================

class TestNewmanResult:
    """Tests for NewmanResult dataclass."""

    def test_newman_result_defaults(self):
        """NewmanResult has sensible defaults."""
        result = NewmanResult(
            success=True,
            total_requests=5,
            failed_requests=0,
            total_assertions=10,
            failed_assertions=0,
            duration_ms=1000,
        )
        
        assert result.test_results == []
        assert result.error_message is None
        assert result.raw_report is None

    def test_newman_result_with_test_results(self):
        """NewmanResult can contain test results."""
        test_results = [
            TestResult(name="Test 1", status="passed", duration_ms=100),
            TestResult(name="Test 2", status="failed", duration_ms=200, error_message="Error"),
        ]
        
        result = NewmanResult(
            success=False,
            total_requests=2,
            failed_requests=1,
            total_assertions=2,
            failed_assertions=1,
            duration_ms=300,
            test_results=test_results,
        )
        
        assert len(result.test_results) == 2
        assert result.test_results[0].name == "Test 1"
