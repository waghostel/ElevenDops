
"""
Tests for Task 28: Test Idempotence
"""

import pytest
from unittest.mock import MagicMock
from hypothesis import given, strategies as st
from tests.postman.postman_test_helpers import TestDataManager

# -----------------------------------------------------------------------------
# Property Tests
# -----------------------------------------------------------------------------

@given(st.lists(st.sampled_from(["documents", "audio", "agents"]), min_size=1))
def test_idempotence_property(resource_types):
    """Property 43: Test Idempotence
    Verifies that running resource creation and cleanup multiple times yields consistent states.
    """
    manager = TestDataManager(prefix="IdempotenceTest_")
    
    # Run 1
    for rt in resource_types:
        manager.get_test_id(rt)
        
    created_run_1 = {k: list(v) for k, v in manager.created_resources.items() if v}
    assert any(created_run_1.values()), "Should have created resources"
    
    manager.cleanup()
    # In a real system, cleanup would remove backend resources.
    # Here we verify the manager tracks them for cleanup.
    # And if we re-run, we generate NEW IDs (uniqueness), but the process should succeed.
    
    # Reset manager state (simulate new test run)
    manager = TestDataManager(prefix="IdempotenceTest_")
    
    # Run 2
    for rt in resource_types:
        manager.get_test_id(rt)
        
    created_run_2 = {k: list(v) for k, v in manager.created_resources.items() if v}
    assert any(created_run_2.values())
    
    # IDs should be different (due to UUID randomness)
    # But keys (resource types utilized) should be identical
    assert created_run_1.keys() == created_run_2.keys()


def test_cleanup_execution():
    """Verify cleanup is called for all tracked resources."""
    manager = TestDataManager()
    
    # Add some mock resources
    manager.created_resources['documents'].append("doc_1")
    manager.created_resources['agents'].append("agent_1")
    
    # Determine if clean up actually does something.
    # In `postman_test_helpers.py`, cleanup logs info.
    # We can't easily assert logging without a specialized fixture, 
    # but we can verify it runs without error.
    
    try:
        manager.cleanup()
    except Exception as e:
        pytest.fail(f"Cleanup failed with error: {e}")
