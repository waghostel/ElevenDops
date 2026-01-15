"""
Task 4: Backend Health Verification Tests

This test file validates backend health verification functionality:
- Health check utility with retry logic
- Exponential backoff implementation
- Property tests for health verification
- Unit tests for edge cases
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
from pathlib import Path

from hypothesis import given, strategies as st

from postman_test_helpers import (
    TestDataManager,
    log_test_info,
)

# Import backend modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.health_check_service import (
    HealthCheckService,
    check_backend_health,
)


class TestHealthCheckServiceInitialization:
    """Test HealthCheckService initialization."""
    
    def test_service_initialization_defaults(self):
        """Test creating HealthCheckService with defaults."""
        service = HealthCheckService()
        
        assert service.base_url == "http://localhost:8000"
        assert service.timeout == 5
        assert service.max_retries == 3
        assert service.backoff_factor == 2.0
    
    def test_service_initialization_custom_values(self):
        """Test creating HealthCheckService with custom values."""
        service = HealthCheckService(
            base_url="https://api.example.com",
            timeout=10,
            max_retries=5,
            backoff_factor=1.5,
        )
        
        assert service.base_url == "https://api.example.com"
        assert service.timeout == 10
        assert service.max_retries == 5
        assert service.backoff_factor == 1.5


class TestHealthCheckBasic:
    """Test basic health check functionality."""
    
    @patch('backend.services.health_check_service.httpx.Client')
    def test_health_check_success(self, mock_client_class):
        """Test successful health check."""
        # Mock the HTTP client
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get = Mock(return_value=mock_response)
        
        mock_client_class.return_value = mock_client
        
        service = HealthCheckService()
        result = service.check_health()
        
        assert result["status"] == "healthy"
        assert result["healthy"] is True
        assert result["status_code"] == 200
    
    @patch('backend.services.health_check_service.httpx.Client')
    def test_health_check_failure(self, mock_client_class):
        """Test failed health check."""
        # Mock the HTTP client to raise exception
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get = Mock(side_effect=Exception("Connection failed"))
        
        mock_client_class.return_value = mock_client
        
        service = HealthCheckService(max_retries=1)
        result = service.check_health()
        
        assert result["status"] == "unhealthy"
        assert result["healthy"] is False
        assert "error" in result
    
    @patch('backend.services.health_check_service.httpx.Client')
    def test_health_check_with_retry(self, mock_client_class):
        """Test health check with retry logic."""
        # Mock the HTTP client to fail first, then succeed
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        
        # First call fails, second succeeds
        mock_client.get = Mock(
            side_effect=[
                Exception("Connection failed"),
                mock_response,
            ]
        )
        
        mock_client_class.return_value = mock_client
        
        service = HealthCheckService(max_retries=2)
        result = service.check_health()
        
        assert result["status"] == "healthy"
        assert result["healthy"] is True


class TestHealthCheckRetryLogic:
    """Test retry logic with exponential backoff."""
    
    def test_backoff_calculation(self):
        """Test exponential backoff calculation."""
        service = HealthCheckService(backoff_factor=2.0)
        
        assert service._calculate_backoff(0) == 1.0
        assert service._calculate_backoff(1) == 2.0
        assert service._calculate_backoff(2) == 4.0
        assert service._calculate_backoff(3) == 8.0
    
    def test_backoff_with_different_factor(self):
        """Test backoff with different factor."""
        service = HealthCheckService(backoff_factor=1.5)
        
        assert service._calculate_backoff(0) == 1.0
        assert service._calculate_backoff(1) == 1.5
        assert service._calculate_backoff(2) == 2.25
    
    @patch('backend.services.health_check_service.time.sleep')
    @patch('backend.services.health_check_service.httpx.Client')
    def test_retry_with_backoff_timing(self, mock_client_class, mock_sleep):
        """Test that backoff timing is applied."""
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        
        # Fail twice, then succeed
        mock_client.get = Mock(
            side_effect=[
                Exception("Connection failed"),
                Exception("Connection failed"),
                mock_response,
            ]
        )
        
        mock_client_class.return_value = mock_client
        
        service = HealthCheckService(max_retries=3, backoff_factor=2.0)
        result = service.check_health()
        
        # Verify sleep was called with correct backoff times
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1.0)
        mock_sleep.assert_any_call(2.0)
    
    @patch('backend.services.health_check_service.httpx.Client')
    def test_max_retries_exceeded(self, mock_client_class):
        """Test behavior when max retries exceeded."""
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get = Mock(side_effect=Exception("Connection failed"))
        
        mock_client_class.return_value = mock_client
        
        service = HealthCheckService(max_retries=2)
        result = service.check_health()
        
        assert result["status"] == "unhealthy"
        assert result["healthy"] is False
        assert result["attempts"] == 3  # 0, 1, 2


class TestHealthCheckReadiness:
    """Test readiness check."""
    
    @patch('backend.services.health_check_service.httpx.Client')
    def test_readiness_check_ready(self, mock_client_class):
        """Test readiness check when backend is ready."""
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get = Mock(return_value=mock_response)
        
        mock_client_class.return_value = mock_client
        
        service = HealthCheckService()
        result = service.check_readiness()
        
        assert result["status"] == "ready"
        assert result["ready"] is True
    
    @patch('backend.services.health_check_service.httpx.Client')
    def test_readiness_check_not_ready(self, mock_client_class):
        """Test readiness check when backend is not ready."""
        mock_response = Mock()
        mock_response.status_code = 503
        
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get = Mock(return_value=mock_response)
        
        mock_client_class.return_value = mock_client
        
        service = HealthCheckService()
        result = service.check_readiness()
        
        assert result["status"] == "not_ready"
        assert result["ready"] is False
    
    @patch('backend.services.health_check_service.httpx.Client')
    def test_readiness_check_error(self, mock_client_class):
        """Test readiness check with error."""
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get = Mock(side_effect=Exception("Connection error"))
        
        mock_client_class.return_value = mock_client
        
        service = HealthCheckService()
        result = service.check_readiness()
        
        assert result["status"] == "not_ready"
        assert result["ready"] is False
        assert "error" in result


class TestHealthCheckServiceStatus:
    """Test service status check."""
    
    @patch('backend.services.health_check_service.httpx.Client')
    def test_service_status_available(self, mock_client_class):
        """Test service status when available."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={"total": 10, "passed": 10})
        
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get = Mock(return_value=mock_response)
        
        mock_client_class.return_value = mock_client
        
        service = HealthCheckService()
        result = service.check_service_status()
        
        assert result["status"] == "available"
        assert result["available"] is True
        assert "data" in result
    
    @patch('backend.services.health_check_service.httpx.Client')
    def test_service_status_unavailable(self, mock_client_class):
        """Test service status when unavailable."""
        mock_response = Mock()
        mock_response.status_code = 500
        
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get = Mock(return_value=mock_response)
        
        mock_client_class.return_value = mock_client
        
        service = HealthCheckService()
        result = service.check_service_status()
        
        assert result["status"] == "unavailable"
        assert result["available"] is False


class TestHealthCheckFullCheck:
    """Test full health check."""
    
    @patch('backend.services.health_check_service.httpx.Client')
    def test_full_health_check_all_healthy(self, mock_client_class):
        """Test full health check when all services are healthy."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json = Mock(return_value={"status": "ok"})
        
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get = Mock(return_value=mock_response)
        
        mock_client_class.return_value = mock_client
        
        service = HealthCheckService()
        result = service.full_health_check()
        
        assert result["overall_healthy"] is True
        assert result["overall_status"] == "healthy"
        assert "health" in result
        assert "readiness" in result
        assert "service" in result
    
    @patch('backend.services.health_check_service.httpx.Client')
    def test_full_health_check_partial_failure(self, mock_client_class):
        """Test full health check with partial failure."""
        # Mock responses: health OK, readiness fails, service OK
        responses = [
            Mock(status_code=200),  # health
            Mock(status_code=503),  # readiness
            Mock(status_code=200, json=Mock(return_value={})),  # service
        ]
        
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get = Mock(side_effect=responses)
        
        mock_client_class.return_value = mock_client
        
        service = HealthCheckService()
        result = service.full_health_check()
        
        assert result["overall_healthy"] is False
        assert result["overall_status"] == "unhealthy"


class TestHealthCheckConvenienceFunction:
    """Test convenience function."""
    
    @patch('backend.services.health_check_service.httpx.Client')
    def test_check_backend_health_function(self, mock_client_class):
        """Test check_backend_health convenience function."""
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get = Mock(return_value=mock_response)
        
        mock_client_class.return_value = mock_client
        
        result = check_backend_health()
        
        assert result["status"] == "healthy"
        assert result["healthy"] is True


class TestBackendHealthVerificationProperty:
    """Property tests for backend health verification."""
    
    @given(
        base_url=st.just("http://localhost:8000"),
        timeout=st.integers(min_value=1, max_value=30),
        max_retries=st.integers(min_value=0, max_value=5),
    )
    @patch('backend.services.health_check_service.httpx.Client')
    def test_property_health_check_consistency(
        self,
        mock_client_class,
        base_url,
        timeout,
        max_retries,
    ):
        """
        Property 1: Backend Health Verification
        
        Validates: Requirements 1.1
        
        For any valid health check configuration:
        1. Service should initialize successfully
        2. Health check should return consistent structure
        3. Result should have required fields
        4. Status should be either 'healthy' or 'unhealthy'
        """
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get = Mock(return_value=mock_response)
        
        mock_client_class.return_value = mock_client
        
        # Property 1: Service initializes successfully
        service = HealthCheckService(
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )
        assert service is not None
        
        # Property 2: Health check returns consistent structure
        result = service.check_health()
        assert isinstance(result, dict)
        
        # Property 3: Result has required fields
        assert "status" in result
        assert "healthy" in result
        
        # Property 4: Status is valid
        assert result["status"] in ["healthy", "unhealthy"]
        assert isinstance(result["healthy"], bool)


class TestHealthCheckEdgeCases:
    """Test edge cases in health check."""
    
    @patch('backend.services.health_check_service.httpx.Client')
    def test_health_check_timeout(self, mock_client_class):
        """Test health check with timeout."""
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        
        import httpx
        mock_client.get = Mock(side_effect=httpx.TimeoutException("Timeout"))
        
        mock_client_class.return_value = mock_client
        
        service = HealthCheckService(max_retries=1)
        result = service.check_health()
        
        assert result["status"] == "unhealthy"
        assert result["healthy"] is False
    
    @patch('backend.services.health_check_service.httpx.Client')
    def test_health_check_connection_error(self, mock_client_class):
        """Test health check with connection error."""
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        
        import httpx
        mock_client.get = Mock(side_effect=httpx.ConnectError("Connection refused"))
        
        mock_client_class.return_value = mock_client
        
        service = HealthCheckService(max_retries=1)
        result = service.check_health()
        
        assert result["status"] == "unhealthy"
        assert result["healthy"] is False
    
    @patch('backend.services.health_check_service.httpx.Client')
    def test_health_check_unexpected_status_code(self, mock_client_class):
        """Test health check with unexpected status code."""
        mock_response = Mock()
        mock_response.status_code = 500
        
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get = Mock(return_value=mock_response)
        
        mock_client_class.return_value = mock_client
        
        service = HealthCheckService(max_retries=1)
        result = service.check_health()
        
        assert result["status"] == "unhealthy"
        assert result["healthy"] is False


class TestHealthCheckCustomConfiguration:
    """Test health check with custom configuration."""
    
    @patch('backend.services.health_check_service.httpx.Client')
    def test_health_check_custom_base_url(self, mock_client_class):
        """Test health check with custom base URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get = Mock(return_value=mock_response)
        
        mock_client_class.return_value = mock_client
        
        service = HealthCheckService(base_url="https://api.example.com")
        result = service.check_health()
        
        assert result["status"] == "healthy"
        # Verify the correct URL was called
        mock_client.get.assert_called_with("https://api.example.com/api/health")
    
    @patch('backend.services.health_check_service.httpx.Client')
    def test_health_check_custom_timeout(self, mock_client_class):
        """Test health check with custom timeout."""
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get = Mock(return_value=mock_response)
        
        mock_client_class.return_value = mock_client
        
        service = HealthCheckService(timeout=15)
        result = service.check_health()
        
        assert result["status"] == "healthy"
        # Verify timeout was set
        mock_client_class.assert_called_with(timeout=15)


@pytest.mark.postman
@pytest.mark.property
class TestHealthCheckProperties:
    """Property-based tests for health check."""
    
    @patch('backend.services.health_check_service.httpx.Client')
    def test_property_health_check_idempotence(self, mock_client_class):
        """Test that health check is idempotent."""
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get = Mock(return_value=mock_response)
        
        mock_client_class.return_value = mock_client
        
        service = HealthCheckService()
        
        # Run health check multiple times
        result1 = service.check_health()
        result2 = service.check_health()
        result3 = service.check_health()
        
        # Results should be consistent
        assert result1["status"] == result2["status"] == result3["status"]
        assert result1["healthy"] == result2["healthy"] == result3["healthy"]
