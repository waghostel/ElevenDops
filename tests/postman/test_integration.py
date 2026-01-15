
"""
Tests for Task 30: Final Integration Testing
"""

import pytest
from unittest.mock import MagicMock, patch
from tests.postman.cli_runner import run_tests, parse_args

def test_integration_full_suite_execution():
    """Test 30.1 & 30.2: Run complete test suite."""
    with patch('tests.postman.cli_runner.TestOrchestrator') as mock_orch_cls, \
         patch('tests.postman.cli_runner.ResultsReporter') as mock_rep_cls:
        
        mock_orch = mock_orch_cls.return_value
        mock_rep = mock_rep_cls.return_value
        
        # Simulate successful run
        mock_orch.verify_backend_health.return_value = True
        result_ok = MagicMock()
        result_ok.is_success = True
        mock_orch.run_test_collection.return_value = [result_ok, result_ok]
        
        args = parse_args(['run', '--check-health'])
        
        # Run
        run_tests(args)
        
        # Verify
        mock_orch.verify_backend_health.assert_called()
        mock_orch.run_test_collection.assert_called()
        mock_rep.generate_summary.assert_called()

def test_integration_cleanup_verification():
    """Test 30.3: Verify cleanup execution."""
    # This logic is mostly covered by Task 28 idempotence tests.
    # Here we ensure CLI 'cleanup' command invokes manager.cleanup
    from tests.postman.cli_runner import cleanup_environment
    
    with patch('tests.postman.cli_runner.TestDataManager') as mock_manager_cls:
        mock_mgr = mock_manager_cls.return_value
        
        # Run cleanup
        cleanup_environment(MagicMock())
        
        mock_mgr.cleanup.assert_called_once()
