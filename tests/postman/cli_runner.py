"""
CLI Runner for Postman Backend Testing.

This module provides a command-line interface to orchestrate Postman tests,
manage resources, and generate reports.
"""

import argparse
import sys
import logging
from typing import List, Optional

from .test_orchestrator import TestOrchestrator
from .results_reporter import ResultsReporter
from .postman_test_helpers import TestDataManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_environment(args: argparse.Namespace) -> None:
    """Initialize test environment."""
    logger.info("Setting up test environment...")
    # In real impl, this might create initial resources or check deps
    orchestrator = TestOrchestrator()
    if orchestrator.activate_postman_power():
        logger.info("Environment setup complete.")
    else:
        logger.error("Failed to setup environment.")
        sys.exit(1)


def cleanup_environment(args: argparse.Namespace) -> None:
    """Clean up test resources."""
    logger.info("Cleaning up test environment...")
    manager = TestDataManager()
    # In a real CLI, we might need a way to target specific existing resources
    # for now we call cleanup on the manager (which cleans its own session resources)
    manager.cleanup()
    logger.info("Cleanup complete.")


def run_tests(args: argparse.Namespace) -> None:
    """Execute tests based on arguments."""
    orchestrator = TestOrchestrator()
    
    if args.check_health:
        if not orchestrator.verify_backend_health():
            logger.error("Backend health check failed. Aborting.")
            sys.exit(1)

    results = []
    if args.folder:
        results = orchestrator.run_test_folder(args.folder)
    else:
        results = orchestrator.run_test_collection()
        
    reporter = ResultsReporter(output_file=args.report)
    reporter.generate_summary(results)
    reporter.update_config_file(results)
    
    # Exit code based on success
    success = all(r.is_success for r in results)
    if not success:
        sys.exit(1)


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Postman Backend Test Runner")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Run command
    run_parser = subparsers.add_parser('run', help='Run tests')
    run_parser.add_argument('--folder', '-f', help='Specific folder to run')
    run_parser.add_argument('--report', '-r', default='test_report.md', help='Report output file')
    run_parser.add_argument('--check-health', action='store_true', help='Verify backend health before running')
    run_parser.set_defaults(func=run_tests)

    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup test environment')
    setup_parser.set_defaults(func=setup_environment)

    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Cleanup test resources')
    cleanup_parser.set_defaults(func=cleanup_environment)

    return parser.parse_args(args)


def main() -> None:
    args = parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parse_args(['--help'])


if __name__ == '__main__':
    main()
