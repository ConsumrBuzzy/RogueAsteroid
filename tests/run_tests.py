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
             category: Optional[str] = None,
             failfast: bool = False) -> int:
    """Run tests with optional coverage reporting.
    
    Args:
        test_paths: List of test paths to run, or None for all tests
        coverage_enabled: Whether to enable coverage reporting
        verbose: Whether to show verbose output
        category: Test category to run (unit, integration, etc.)
        failfast: Stop on first failure
        
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
                '*/conftest.py'
            ]
        )
        cov.start()

    # Build pytest arguments
    pytest_args = []
    
    # Add verbosity
    if verbose:
        pytest_args.append('-v')
        
    # Add test category marker
    if category:
        pytest_args.extend(['-m', category])
        
    # Add failfast
    if failfast:
        pytest_args.append('-x')
        
    # Add test paths
    if test_paths:
        pytest_args.extend(test_paths)
        
    # Add coverage options
    if coverage_enabled:
        pytest_args.extend(['--cov=src', '--cov-report=term-missing'])

    # Run tests
    result = pytest.main(pytest_args)

    if coverage_enabled:
        # Stop coverage tracking
        cov.stop()
        
        # Generate reports
        print("\nCoverage Report:")
        cov.report(show_missing=True)
        
        # Generate HTML report
        html_dir = os.path.join('tests', 'coverage', 'html')
        os.makedirs(html_dir, exist_ok=True)
        cov.html_report(directory=html_dir)
        
        print(f"\nDetailed coverage report: {os.path.join(html_dir, 'index.html')}")

    return result

def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description='Run RogueAsteroid tests')
    
    parser.add_argument('paths', nargs='*', help='Test paths to run')
    parser.add_argument('--no-cov', action='store_true', help='Disable coverage reporting')
    parser.add_argument('-q', '--quiet', action='store_true', help='Decrease verbosity')
    parser.add_argument('-m', '--marker', help='Only run tests with this marker')
    parser.add_argument('-x', '--failfast', action='store_true', help='Stop on first failure')
    
    args = parser.parse_args()
    
    result = run_tests(
        test_paths=args.paths if args.paths else None,
        coverage_enabled=not args.no_cov,
        verbose=not args.quiet,
        category=args.marker,
        failfast=args.failfast
    )
    
    sys.exit(result)

if __name__ == '__main__':
    main() 