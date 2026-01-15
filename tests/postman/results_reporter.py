"""
Results Reporter Component for Postman Backend Testing.

This module processes test results, generates summaries, and updates configuration
with execution metrics.

Supports both internal TestResult objects and external Newman JSON reports.
"""

import logging
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from .test_orchestrator import TestResult
from .postman_test_helpers import PostmanConfigHelper

# Configure logging
logger = logging.getLogger(__name__)


class ResultsReporter:
    """Handles reporting of Postman test results.
    
    Supports:
    - Internal TestResult objects from TestOrchestrator
    - External Newman JSON report files for CI/CD integration
    """
    
    def __init__(self, output_file: str = "test_report.md"):
        self.output_file = output_file
        
    def parse_results(self, results: List[TestResult]) -> Dict[str, Any]:
        """
        Parse raw results into a summary structure.
        
        Args:
            results: List of TestResult objects.
            
        Returns:
            Dict containing summary metrics and categorized lists.
        """
        total = len(results)
        passed = sum(1 for r in results if r.is_success)
        failed = sum(1 for r in results if not r.is_success)
        duration = sum(r.duration_ms for r in results)
        
        failures = [
            {
                "name": r.name,
                "error": r.error_message,
                "assertions": r.assertions
            }
            for r in results if not r.is_success
        ]
        
        return {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failed,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "total_duration_ms": duration,
            "failures": failures,
            "timestamp": datetime.now().isoformat()
        }
    
    def parse_newman_report(self, report_path: str) -> List[TestResult]:
        """Parse a Newman JSON report file into TestResult objects.
        
        This allows generating summaries from offline Newman runs or CI artifacts.
        
        Args:
            report_path: Path to Newman JSON report file.
            
        Returns:
            List[TestResult]: Parsed test results.
            
        Raises:
            FileNotFoundError: If report file doesn't exist.
            json.JSONDecodeError: If report is not valid JSON.
        """
        if not os.path.exists(report_path):
            raise FileNotFoundError(f"Newman report not found: {report_path}")
        
        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)
        
        run_data = report.get("run", {})
        executions = run_data.get("executions", [])
        
        results = []
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
            
            results.append(
                TestResult(
                    name=item.get("name", "Unknown Request"),
                    status=status,
                    duration_ms=response.get("responseTime", 0),
                    error_message=error_msg,
                    assertions=assertion_dict,
                )
            )
        
        logger.info(f"Parsed {len(results)} test results from Newman report")
        return results
        
    def generate_summary(self, results: List[TestResult]) -> str:
        """
        Generate a human-readable markdown summary.
        
        Args:
            results: List of TestResult objects.
            
        Returns:
            String containing markdown report.
        """
        metrics = self.parse_results(results)
        
        lines = [
            "# Postman Test Run Summary",
            f"**Date:** {metrics['timestamp']}",
            "",
            "## Overview",
            f"- **Total Tests:** {metrics['total_tests']}",
            f"- **Passed:** {metrics['passed_tests']}",
            f"- **Failed:** {metrics['failed_tests']}",
            f"- **Duration:** {metrics['total_duration_ms']:.2f}ms",
            f"- **Success Rate:** {metrics['success_rate']:.1f}%",
            "",
        ]
        
        if metrics['failures']:
            lines.append("## Failures")
            for fail in metrics['failures']:
                lines.append(f"### {fail['name']}")
                lines.append(f"- **Error:** {fail.get('error') or 'Unknown error'}")
                if fail['assertions']:
                    lines.append("- **Failed Assertions:**")
                    for name, passed in fail['assertions'].items():
                        if not passed:
                            lines.append(f"  - [x] {name}")
                lines.append("")
        else:
            lines.append("## Status")
            lines.append("✅ All tests passed!")
            
        report = "\n".join(lines)
        
        # Optionally write to file
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Report written to {self.output_file}")
        except Exception as e:
            logger.error(f"Failed to write report: {e}")
            
        return report
    
    def generate_summary_from_newman_report(self, report_path: str) -> str:
        """Generate summary directly from a Newman JSON report file.
        
        Convenience method that combines parse_newman_report and generate_summary.
        
        Args:
            report_path: Path to Newman JSON report file.
            
        Returns:
            String containing markdown report.
        """
        results = self.parse_newman_report(report_path)
        return self.generate_summary(results)

    def update_config_file(self, results: List[TestResult]) -> None:
        """
        Update local Postman config with last run stats.
        
        Args:
            results: List of TestResult objects.
        """
        metrics = self.parse_results(results)
        
        update = {
            "last_run": {
                "timestamp": metrics['timestamp'],
                "passed": metrics['passed_tests'],
                "failed": metrics['failed_tests'],
                "total": metrics['total_tests']
            }
        }
        
        PostmanConfigHelper.update_config(update)

