"""
Results Reporter Component for Postman Backend Testing.

This module processes test results, generates summaries, and updates configuration
with execution metrics.
"""

import logging
import json
from datetime import datetime
from typing import List, Dict, Any

from .test_orchestrator import TestResult
from .postman_test_helpers import PostmanConfigHelper

# Configure logging
logger = logging.getLogger(__name__)


class ResultsReporter:
    """Handles reporting of Postman test results."""
    
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
