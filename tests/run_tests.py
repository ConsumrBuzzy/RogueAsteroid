#!/usr/bin/env python3
"""Test runner for RogueAsteroid with coverage reporting."""
import os
import sys
import pytest
import coverage
import argparse
from typing import List, Optional

def run_tests(test_paths: Optional[List[str]] = None, 
             coverage_enabled: bool = True,
             verbose: bool = True,
             category: Optional[str] = None) -> int:
    """Run tests with optional coverage reporting.
    
    Args:
        test_paths: List of test paths to run, or None for all tests
        coverage_enabled: Whether to enable coverage reporting
        verbose: Whether to show verbose output
        category: Test category to run (unit, integration, etc.)
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    if coverage_enabled:
        # Start coverage tracking
        cov = coverage.Coverage(
            branch=True,
            source=['src'],
            omit=[
                '*/test_*.py',
                '*/__init__.py',
                '*/setup.py',
            ]
        )
        cov.start()

    # Build pytest arguments
    pytest_args = []
    if verbose:
        pytest_args.append('-v')
    if category:
        pytest_args.extend(['-m', category])
    if test_paths:
        pytest_args.extend(test_paths)

    # Run tests
    result = pytest.main(pytest_args)

    if coverage_enabled:
        # Stop coverage tracking and generate report
        cov.stop()
        cov.save()
        
        print("\nCoverage Report:")
        cov.report()
        
        # Generate HTML report
        html_dir = os.path.join('tests', 'coverage')
        cov.html_report(directory=html_dir)
        print(f"\nDetailed coverage report: {html_dir}/index.html")

    return result

def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description='Run RogueAsteroid tests')
    parser.add_argument('--no-coverage', action='store_true',
                      help='Disable coverage reporting')
    parser.add_argument('-q', '--quiet', action='store_true',
                      help='Reduce output verbosity')
    parser.add_argument('-k', '--filter', type=str,
                      help='Only run tests matching given substring expression')
    parser.add_argument('-m', '--marker', type=str, choices=['unit', 'integration', 'component', 'gameplay'],
                      help='Only run tests with specific marker')
    parser.add_argument('test_paths', nargs='*',
                      help='Specific test paths to run')
    
    args = parser.parse_args()
    
    # Set up test paths
    test_paths = args.test_paths if args.test_paths else None
    if args.filter:
        if not test_paths:
            test_paths = []
        test_paths.extend(['-k', args.filter])
    
    # Run tests
    result = run_tests(
        test_paths=test_paths,
        coverage_enabled=not args.no_coverage,
        verbose=not args.quiet,
        category=args.marker
    )
    
    sys.exit(result)

if __name__ == '__main__':
    main() 