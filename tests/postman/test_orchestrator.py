"""
Test Orchestrator Component for Postman Backend Testing.

This module is responsible for coordinating the execution of Postman tests,
interacting with Postman Power, and managing the test lifecycle.

Supports two execution modes:
- Simulation (default): Returns mock results for testing orchestration logic
- Newman: Executes real collections via Newman CLI for E2E verification
"""

import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from .postman_test_helpers import HealthCheckHelper, PostmanConfigHelper

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Represents the result of a single test or collection run."""
    name: str
    status: str  # 'passed', 'failed', 'error'
    duration_ms: float
    error_message: Optional[str] = None
    assertions: Dict[str, bool] = field(default_factory=dict)
    
    @property
    def is_success(self) -> bool:
        return self.status == 'passed'


class TestOrchestrator:
    """Orchestrates the execution of Postman backend tests.
    
    Supports two execution modes:
    - use_newman=False (default): Simulated execution for unit testing
    - use_newman=True: Real execution via Newman CLI for E2E testing
    """
    
    def __init__(
        self, 
        config: Optional[Dict[str, Any]] = None,
        use_newman: bool = False,
        newman_timeout: int = 120,
    ):
        """Initialize TestOrchestrator.
        
        Args:
            config: Postman configuration dict. Defaults to loading from config file.
            use_newman: If True, use Newman CLI for real execution. Default False.
            newman_timeout: Timeout in seconds for Newman runs. Default 120.
        """
        self.config = config if config is not None else PostmanConfigHelper.load_config()
        self.results: List[TestResult] = []
        self._postman_power_active = False
        self._use_newman = use_newman
        self._newman_runner = None
        
        if use_newman:
            self._init_newman_runner(newman_timeout)
    
    def _init_newman_runner(self, timeout: int) -> None:
        """Lazily initialize Newman runner."""
        try:
            from .newman_runner import NewmanRunner
            self._newman_runner = NewmanRunner(timeout=timeout)
            if self._newman_runner.is_newman_installed():
                logger.info("Newman runner initialized successfully.")
            else:
                logger.warning("Newman not installed. Will fall back to simulation.")
        except ImportError as e:
            logger.warning(f"Failed to import NewmanRunner: {e}")
            self._newman_runner = None
        
    def activate_postman_power(self) -> bool:
        """
        Initialize and activate the Postman Power client.
        
        Returns:
            bool: True if activation was successful, False otherwise.
        """
        logger.info("Activating Postman Power client...")
        try:
            # In a real implementation, this would connect to the Postman Power daemon/service
            # For now, we simulate success if configuration is present
            if not self.config.get('postman_api_key'):
                 logger.warning("Postman API key missing in config, simulated activation only.")
            
            self._postman_power_active = True
            logger.info("Postman Power client activated.")
            return True
        except Exception as e:
            logger.error(f"Failed to activate Postman Power: {e}")
            self._postman_power_active = False
            return False

    def verify_backend_health(self, timeout: int = 30) -> bool:
        """
        Verify that the backend service is healthy and ready for testing.
        
        Args:
            timeout: Maximum time to wait for health check in seconds.
            
        Returns:
            bool: True if backend is healthy, False otherwise.
        """
        logger.info(f"Verifying backend health (timeout={timeout}s)...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if HealthCheckHelper.is_backend_healthy():
                logger.info("Backend is healthy.")
                return True
            time.sleep(1)
            
        logger.error("Backend health check timed out.")
        return False

    def run_test_collection(
        self, 
        collection_path: Optional[str] = None,
        environment_path: Optional[str] = None,
        collection_id: Optional[str] = None,
        environment_id: Optional[str] = None,
    ) -> List[TestResult]:
        """
        Execute a full Postman collection.
        
        Args:
            collection_path: Path to collection JSON file (for Newman mode).
            environment_path: Path to environment JSON file (for Newman mode).
            collection_id: ID of the collection to run (for Postman API mode).
            environment_id: ID of the environment to use (for Postman API mode).
            
        Returns:
            List[TestResult]: Results of the test run.
        """
        # Try Newman execution if enabled and available
        if self._use_newman and self._newman_runner:
            return self._run_with_newman(collection_path, environment_path)
        
        # Fall back to simulation
        return self._simulate_collection_run(collection_id, environment_id)
    
    def _run_with_newman(
        self, 
        collection_path: Optional[str], 
        environment_path: Optional[str],
        folder: Optional[str] = None,
    ) -> List[TestResult]:
        """Execute collection using Newman CLI.
        
        Args:
            collection_path: Path to collection JSON file.
            environment_path: Path to environment JSON file.
            folder: Optional folder to run within collection.
            
        Returns:
            List[TestResult]: Parsed results from Newman run.
        """
        if not collection_path:
            collection_path = self.config.get('collection_path')
        if not environment_path:
            environment_path = self.config.get('environment_path')
            
        if not collection_path:
            raise ValueError("Collection path required for Newman execution")
        
        logger.info(f"Running collection via Newman: {collection_path}")
        
        result = self._newman_runner.run_collection(
            collection_path=collection_path,
            environment_path=environment_path,
            folder=folder,
        )
        
        if result.error_message:
            logger.error(f"Newman execution error: {result.error_message}")
            # Return error as a single failed test result
            error_result = TestResult(
                name="Newman Execution",
                status="error",
                duration_ms=result.duration_ms,
                error_message=result.error_message,
            )
            self.results.append(error_result)
            return [error_result]
        
        # Log summary
        logger.info(
            f"Newman run complete: {result.total_requests} requests, "
            f"{result.failed_requests} failed, "
            f"{result.total_assertions} assertions, "
            f"{result.failed_assertions} failed"
        )
        
        self.results.extend(result.test_results)
        return result.test_results
    
    def _simulate_collection_run(
        self, 
        collection_id: Optional[str] = None,
        environment_id: Optional[str] = None,
    ) -> List[TestResult]:
        """Simulate collection execution (for testing orchestration logic).
        
        Args:
            collection_id: ID of collection (for logging).
            environment_id: ID of environment (for logging).
            
        Returns:
            List[TestResult]: Simulated results.
        """
        cid = collection_id or self.config.get('collection_id')
        eid = environment_id or self.config.get('environment_id')
        
        if not cid:
            raise ValueError("Collection ID required")
            
        logger.info(f"Running collection {cid} (env: {eid}) [SIMULATED]...")
        
        results = [
            TestResult(name="Collection Run", status="passed", duration_ms=1200)
        ]
        self.results.extend(results)
        return results

    def run_test_folder(
        self, 
        folder_id: str, 
        collection_path: Optional[str] = None,
        environment_path: Optional[str] = None,
        collection_id: Optional[str] = None, 
        environment_id: Optional[str] = None,
    ) -> List[TestResult]:
        """
        Execute a specific folder within a collection.
        
        Args:
            folder_id: ID or name of the folder to run.
            collection_path: Path to collection JSON file (for Newman mode).
            environment_path: Path to environment JSON file (for Newman mode).
            collection_id: ID of the collection (for Postman API mode).
            environment_id: ID of the environment (for Postman API mode).
            
        Returns:
            List[TestResult]: Results of the folder run.
        """
        # Try Newman execution if enabled and available
        if self._use_newman and self._newman_runner:
            return self._run_with_newman(collection_path, environment_path, folder=folder_id)
        
        # Fall back to simulation
        return self._simulate_folder_run(folder_id, collection_id, environment_id)
    
    def _simulate_folder_run(
        self,
        folder_id: str,
        collection_id: Optional[str] = None,
        environment_id: Optional[str] = None,
    ) -> List[TestResult]:
        """Simulate folder execution.
        
        Args:
            folder_id: Folder name or ID.
            collection_id: Collection ID (for logging).
            environment_id: Environment ID (for logging).
            
        Returns:
            List[TestResult]: Simulated results.
        """
        cid = collection_id or self.config.get('collection_id')
        eid = environment_id or self.config.get('environment_id')
        
        if not cid:
            raise ValueError("Collection ID required")
            
        logger.info(f"Running folder {folder_id} in collection {cid} (env: {eid}) [SIMULATED]...")
        
        results = [
            TestResult(name=f"Folder {folder_id} Run", status="passed", duration_ms=450)
        ]
        self.results.extend(results)
        return results

    def update_test_results(self) -> None:
        """
        Capture and store/update the test results in the internal state or external file.
        """
        logger.info(f"Updating test results. Total executed: {len(self.results)}")
        # Logic to persist results could go here, e.g. writing to a JSON report
        pass
    
    @property
    def is_newman_available(self) -> bool:
        """Check if Newman is available for execution."""
        if self._newman_runner is None:
            return False
        return self._newman_runner.is_newman_installed()

