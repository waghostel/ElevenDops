"""
Health Check Service

This module provides backend health verification with retry logic
and exponential backoff.
"""

import logging
import time
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)


class HealthCheckService:
    """Service for checking backend health with retry logic."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: int = 5,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
    ):
        """
        Initialize Health Check Service.
        
        Args:
            base_url: Backend base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        logger.info(
            f"Initialized HealthCheckService: base_url={base_url}, "
            f"timeout={timeout}, max_retries={max_retries}"
        )
    
    def check_health(self) -> Dict[str, Any]:
        """
        Check backend health with retry logic.
        
        Returns:
            Dict containing health status
        """
        logger.info("Starting health check...")
        
        for attempt in range(self.max_retries + 1):
            try:
                return self._check_health_attempt(attempt)
            except Exception as e:
                if attempt < self.max_retries:
                    wait_time = self._calculate_backoff(attempt)
                    logger.warning(
                        f"Health check attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Health check failed after {self.max_retries + 1} attempts")
                    return {
                        "status": "unhealthy",
                        "healthy": False,
                        "error": str(e),
                        "attempts": self.max_retries + 1,
                    }
        
        return {
            "status": "unhealthy",
            "healthy": False,
            "error": "Unknown error",
        }
    
    def _check_health_attempt(self, attempt: int) -> Dict[str, Any]:
        """
        Perform a single health check attempt.
        
        Args:
            attempt: Current attempt number (0-indexed)
        
        Returns:
            Dict containing health status
        
        Raises:
            Exception: If health check fails
        """
        logger.debug(f"Health check attempt {attempt + 1}")
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(f"{self.base_url}/api/health")
                
                if response.status_code == 200:
                    logger.info("Backend health check passed")
                    return {
                        "status": "healthy",
                        "healthy": True,
                        "status_code": response.status_code,
                        "attempts": attempt + 1,
                    }
                else:
                    raise RuntimeError(
                        f"Unexpected status code: {response.status_code}"
                    )
        except httpx.ConnectError as e:
            raise RuntimeError(f"Connection error: {e}")
        except httpx.TimeoutException as e:
            raise RuntimeError(f"Timeout error: {e}")
        except Exception as e:
            raise RuntimeError(f"Health check error: {e}")
    
    def check_readiness(self) -> Dict[str, Any]:
        """
        Check backend readiness.
        
        Returns:
            Dict containing readiness status
        """
        logger.info("Checking backend readiness...")
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(f"{self.base_url}/api/health/ready")
                
                if response.status_code == 200:
                    logger.info("Backend readiness check passed")
                    return {
                        "status": "ready",
                        "ready": True,
                        "status_code": response.status_code,
                    }
                else:
                    logger.warning(f"Backend not ready: {response.status_code}")
                    return {
                        "status": "not_ready",
                        "ready": False,
                        "status_code": response.status_code,
                    }
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return {
                "status": "not_ready",
                "ready": False,
                "error": str(e),
            }
    
    def check_service_status(self) -> Dict[str, Any]:
        """
        Check detailed service status.
        
        Returns:
            Dict containing service status details
        """
        logger.info("Checking service status...")
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(f"{self.base_url}/api/dashboard/stats")
                
                if response.status_code == 200:
                    logger.info("Service status check passed")
                    return {
                        "status": "available",
                        "available": True,
                        "status_code": response.status_code,
                        "data": response.json(),
                    }
                else:
                    logger.warning(f"Service status check failed: {response.status_code}")
                    return {
                        "status": "unavailable",
                        "available": False,
                        "status_code": response.status_code,
                    }
        except Exception as e:
            logger.error(f"Service status check failed: {e}")
            return {
                "status": "unavailable",
                "available": False,
                "error": str(e),
            }
    
    def full_health_check(self) -> Dict[str, Any]:
        """
        Perform a full health check including all endpoints.
        
        Returns:
            Dict containing comprehensive health status
        """
        logger.info("Performing full health check...")
        
        health = self.check_health()
        readiness = self.check_readiness()
        service = self.check_service_status()
        
        overall_healthy = (
            health.get("healthy", False) and
            readiness.get("ready", False) and
            service.get("available", False)
        )
        
        result = {
            "overall_status": "healthy" if overall_healthy else "unhealthy",
            "overall_healthy": overall_healthy,
            "health": health,
            "readiness": readiness,
            "service": service,
        }
        
        logger.info(f"Full health check completed: {result['overall_status']}")
        return result
    
    def _calculate_backoff(self, attempt: int) -> float:
        """
        Calculate exponential backoff time.
        
        Args:
            attempt: Current attempt number (0-indexed)
        
        Returns:
            Backoff time in seconds
        """
        backoff = self.backoff_factor ** attempt
        logger.debug(f"Calculated backoff for attempt {attempt}: {backoff}s")
        return backoff


def check_backend_health(
    base_url: str = "http://localhost:8000",
    timeout: int = 5,
    max_retries: int = 3,
) -> Dict[str, Any]:
    """
    Convenience function to check backend health.
    
    Args:
        base_url: Backend base URL
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
    
    Returns:
        Dict containing health status
    """
    service = HealthCheckService(
        base_url=base_url,
        timeout=timeout,
        max_retries=max_retries,
    )
    return service.check_health()


__all__ = ['HealthCheckService', 'check_backend_health']
