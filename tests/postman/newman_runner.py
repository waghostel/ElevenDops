"""
Newman Runner Component for Postman Backend Testing.

This module provides a wrapper around the Newman CLI for executing
Postman collections and parsing results.
"""

import json
import logging
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional

from .test_orchestrator import TestResult

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class NewmanResult:
    """Represents the result of a Newman collection run."""

    success: bool
    total_requests: int
    failed_requests: int
    total_assertions: int
    failed_assertions: int
    duration_ms: float
    test_results: List[TestResult] = field(default_factory=list)
    error_message: Optional[str] = None
    raw_report: Optional[Dict[str, Any]] = None


class NewmanRunner:
    """Wrapper for Newman CLI execution via subprocess."""

    def __init__(self, timeout: int = 120):
        """Initialize NewmanRunner.

        Args:
            timeout: Maximum execution time in seconds for Newman runs.
        """
        self.timeout = timeout
        self._newman_path: Optional[str] = None

    def is_newman_installed(self) -> bool:
        """Check if Newman CLI is available in PATH.

        Returns:
            bool: True if newman is installed and accessible.
        """
        try:
            self._newman_path = shutil.which("newman")
            if self._newman_path:
                result = subprocess.run(
                    ["newman", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    logger.info(f"Newman version: {result.stdout.strip()}")
                    return True
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            logger.warning(f"Newman not available: {e}")
            return False

    def run_collection(
        self,
        collection_path: str,
        environment_path: Optional[str] = None,
        folder: Optional[str] = None,
        globals_path: Optional[str] = None,
    ) -> NewmanResult:
        """Execute a Postman collection via Newman CLI.

        Args:
            collection_path: Path to the collection JSON file.
            environment_path: Optional path to environment JSON file.
            folder: Optional folder name to run within the collection.
            globals_path: Optional path to globals JSON file.

        Returns:
            NewmanResult: Parsed results from the Newman run.
        """
        if not self.is_newman_installed():
            return NewmanResult(
                success=False,
                total_requests=0,
                failed_requests=0,
                total_assertions=0,
                failed_assertions=0,
                duration_ms=0,
                error_message="Newman CLI is not installed. Run: npm install -g newman",
            )

        # Validate collection path
        if not os.path.exists(collection_path):
            return NewmanResult(
                success=False,
                total_requests=0,
                failed_requests=0,
                total_assertions=0,
                failed_assertions=0,
                duration_ms=0,
                error_message=f"Collection file not found: {collection_path}",
            )

        # Create temp file for JSON report
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as report_file:
            report_path = report_file.name

        try:
            # Build newman command
            cmd = [
                "newman",
                "run",
                collection_path,
                "--reporters",
                "json",
                "--reporter-json-export",
                report_path,
            ]

            if environment_path and os.path.exists(environment_path):
                cmd.extend(["--environment", environment_path])

            if globals_path and os.path.exists(globals_path):
                cmd.extend(["--globals", globals_path])

            if folder:
                cmd.extend(["--folder", folder])

            logger.info(f"Running Newman: {' '.join(cmd)}")

            # Execute Newman
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=os.path.dirname(collection_path) or ".",
            )

            # Parse the JSON report
            if os.path.exists(report_path):
                return self._parse_newman_json_report(report_path)
            else:
                return NewmanResult(
                    success=result.returncode == 0,
                    total_requests=0,
                    failed_requests=0,
                    total_assertions=0,
                    failed_assertions=0,
                    duration_ms=0,
                    error_message=result.stderr if result.returncode != 0 else None,
                )

        except subprocess.TimeoutExpired:
            return NewmanResult(
                success=False,
                total_requests=0,
                failed_requests=0,
                total_assertions=0,
                failed_assertions=0,
                duration_ms=0,
                error_message=f"Newman execution timed out after {self.timeout}s",
            )
        except Exception as e:
            logger.error(f"Newman execution failed: {e}")
            return NewmanResult(
                success=False,
                total_requests=0,
                failed_requests=0,
                total_assertions=0,
                failed_assertions=0,
                duration_ms=0,
                error_message=str(e),
            )
        finally:
            # Cleanup temp report file
            try:
                if os.path.exists(report_path):
                    os.unlink(report_path)
            except OSError:
                pass

    def _parse_newman_json_report(self, report_path: str) -> NewmanResult:
        """Parse Newman JSON reporter output into NewmanResult.

        Args:
            report_path: Path to the Newman JSON report file.

        Returns:
            NewmanResult: Parsed results with TestResult objects.
        """
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)

            run_data = report.get("run", {})
            stats = run_data.get("stats", {})
            timings = run_data.get("timings", {})
            executions = run_data.get("executions", [])

            # Extract stats
            requests_stats = stats.get("requests", {})
            assertions_stats = stats.get("assertions", {})

            total_requests = requests_stats.get("total", 0)
            failed_requests = requests_stats.get("failed", 0)
            total_assertions = assertions_stats.get("total", 0)
            failed_assertions = assertions_stats.get("failed", 0)

            # Calculate duration
            duration_ms = timings.get("completed", 0) - timings.get("started", 0)

            # Parse individual test results
            test_results = []
            for execution in executions:
                item = execution.get("item", {})
                response = execution.get("response", {})
                assertions = execution.get("assertions", [])

                # Build assertions dict
                assertion_dict = {}
                error_msg = None
                for assertion in assertions:
                    assertion_name = assertion.get("assertion", "Unknown")
                    assertion_error = assertion.get("error")
                    assertion_dict[assertion_name] = assertion_error is None
                    if assertion_error:
                        error_msg = assertion_error.get("message", str(assertion_error))

                # Determine overall status
                has_failures = any(not passed for passed in assertion_dict.values())
                status = "failed" if has_failures else "passed"

                test_results.append(
                    TestResult(
                        name=item.get("name", "Unknown Request"),
                        status=status,
                        duration_ms=response.get("responseTime", 0),
                        error_message=error_msg,
                        assertions=assertion_dict,
                    )
                )

            return NewmanResult(
                success=failed_requests == 0 and failed_assertions == 0,
                total_requests=total_requests,
                failed_requests=failed_requests,
                total_assertions=total_assertions,
                failed_assertions=failed_assertions,
                duration_ms=duration_ms,
                test_results=test_results,
                raw_report=report,
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Newman JSON report: {e}")
            return NewmanResult(
                success=False,
                total_requests=0,
                failed_requests=0,
                total_assertions=0,
                failed_assertions=0,
                duration_ms=0,
                error_message=f"Failed to parse report: {e}",
            )
        except Exception as e:
            logger.error(f"Error parsing Newman report: {e}")
            return NewmanResult(
                success=False,
                total_requests=0,
                failed_requests=0,
                total_assertions=0,
                failed_assertions=0,
                duration_ms=0,
                error_message=str(e),
            )


def parse_newman_report_file(report_path: str) -> List[TestResult]:
    """Standalone function to parse a Newman JSON report file.

    This can be used by ResultsReporter or other components to parse
    offline Newman reports.

    Args:
        report_path: Path to Newman JSON report file.

    Returns:
        List[TestResult]: Parsed test results.
    """
    runner = NewmanRunner()
    result = runner._parse_newman_json_report(report_path)
    return result.test_results
