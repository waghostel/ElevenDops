
"""
Tests for Task 27: CLI Test Runner
"""

import sys
import pytest
from unittest.mock import MagicMock, patch
from tests.postman.cli_runner import parse_args, main, run_tests, setup_environment, cleanup_environment

# -----------------------------------------------------------------------------
# Unit Tests
# -----------------------------------------------------------------------------

def test_parse_args_run():
    """Test parsing run command arguments."""
    args = parse_args(['run', '--folder', 'my_folder', '--check-health'])
    assert args.command == 'run'
    assert args.folder == 'my_folder'
    assert args.check_health is True
    assert args.report == 'test_report.md'

def test_parse_args_setup():
    """Test parsing setup command."""
    args = parse_args(['setup'])
    assert args.command == 'setup'

def test_parse_args_cleanup():
    """Test parsing cleanup command."""
    args = parse_args(['cleanup'])
    assert args.command == 'cleanup'

@patch('tests.postman.cli_runner.TestOrchestrator')
@patch('tests.postman.cli_runner.ResultsReporter')
def test_run_tests_collection_success(mock_reporter_cls, mock_orch_cls):
    """Test successful run of full collection."""
    # Setup mocks
    mock_orch = mock_orch_cls.return_value
    mock_result = MagicMock()
    mock_result.is_success = True
    mock_orch.run_test_collection.return_value = [mock_result]
    
    mock_reporter = mock_reporter_cls.return_value
    
    args = MagicMock()
    args.folder = None
    args.check_health = False
    args.report = 'report.md'
    
    # Execute
    run_tests(args)
    
    # Verify
    mock_orch.run_test_collection.assert_called_once()
    mock_reporter.generate_summary.assert_called_once()
    mock_reporter.update_config_file.assert_called_once()

@patch('tests.postman.cli_runner.TestOrchestrator')
@patch('tests.postman.cli_runner.ResultsReporter')
def test_run_tests_folder_success(mock_reporter_cls, mock_orch_cls):
    """Test successful run of specific folder."""
    mock_orch = mock_orch_cls.return_value
    mock_result = MagicMock()
    mock_result.is_success = True
    mock_orch.run_test_folder.return_value = [mock_result]
    
    args = MagicMock()
    args.folder = 'my_folder'
    args.check_health = False
    args.report = 'report.md'
    
    run_tests(args)
    
    mock_orch.run_test_folder.assert_called_with('my_folder')

@patch('tests.postman.cli_runner.TestOrchestrator')
def test_run_tests_health_check_fail(mock_orch_cls):
    """Test run fails if health check fails."""
    mock_orch = mock_orch_cls.return_value
    mock_orch.verify_backend_health.return_value = False
    
    args = MagicMock()
    args.check_health = True
    
    with pytest.raises(SystemExit) as exc:
        run_tests(args)
    assert exc.value.code == 1

@patch('tests.postman.cli_runner.TestOrchestrator')
@patch('tests.postman.cli_runner.ResultsReporter')
def test_run_tests_failure_exit_code(mock_reporter_cls, mock_orch_cls):
    """Test run exits with 1 if tests fail."""
    mock_orch = mock_orch_cls.return_value
    mock_result = MagicMock()
    mock_result.is_success = False  # Failure
    mock_orch.run_test_collection.return_value = [mock_result]
    
    args = MagicMock()
    args.folder = None
    args.check_health = False
    args.report = 'report.md'
    
    with pytest.raises(SystemExit) as exc:
        run_tests(args)
    assert exc.value.code == 1

@patch('tests.postman.cli_runner.TestOrchestrator')
def test_setup_environment(mock_orch_cls):
    """Test setup environment."""
    mock_orch = mock_orch_cls.return_value
    mock_orch.activate_postman_power.return_value = True
    
    setup_environment(MagicMock())
    mock_orch.activate_postman_power.assert_called_once()

@patch('tests.postman.cli_runner.TestDataManager')
def test_cleanup_environment(mock_manager_cls):
    """Test cleanup environment."""
    mock_manager = mock_manager_cls.return_value
    
    cleanup_environment(MagicMock())
    mock_manager.cleanup.assert_called_once()
