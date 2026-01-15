"""Fixtures for contract tests validating DataService implementations."""

import pytest
from typing import Generator

from backend.services.data_service import MockDataService, DataServiceInterface
from backend.services.firestore_data_service import FirestoreDataService


@pytest.fixture
def mock_data_service() -> MockDataService:
    """Provide a fresh MockDataService instance for each test."""
    return MockDataService()


@pytest.fixture
def firestore_data_service() -> DataServiceInterface:
    """Provide FirestoreDataService instance, skipping if emulator unavailable."""
    try:
        # Reset singleton for clean state
        FirestoreDataService._instance = None
        service = FirestoreDataService()
        return service
    except Exception as e:
        if "credentials" in str(e).lower() or "connect" in str(e).lower():
            pytest.skip(f"Firestore emulator not available: {e}")
        raise


@pytest.fixture(params=["mock", "firestore"])
def data_service(request) -> DataServiceInterface:
    """Parametrized fixture that runs tests against both implementations."""
    if request.param == "mock":
        return MockDataService()
    else:
        try:
            FirestoreDataService._instance = None
            return FirestoreDataService()
        except Exception as e:
            if "credentials" in str(e).lower() or "connect" in str(e).lower():
                pytest.skip(f"Firestore emulator not available: {e}")
            raise
