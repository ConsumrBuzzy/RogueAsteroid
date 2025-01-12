#!/usr/bin/env python3
"""
Test runner for RogueAsteroid
Supports running tests by category and generating coverage reports
"""

import sys
import pytest
import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description='Run RogueAsteroid tests')
    parser.add_argument('--category', '-c', choices=['unit', 'engine', 'game', 'ui', 'integration', 'all'],
                      default='all', help='Test category to run')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    return parser.parse_args()

def run_tests(category='all', coverage=False, verbose=False):
    """Run tests based on category and options"""
    test_path = Path(__file__).parent
    
    # Build pytest arguments
    pytest_args = []
    
    # Add category marker if not 'all'
    if category != 'all':
        pytest_args.extend(['-m', category])
    
    # Add coverage if requested
    if coverage:
        pytest_args.extend(['--cov=src', '--cov-report=html', '--cov-report=term'])
    
    # Add verbosity
    if verbose:
        pytest_args.append('-v')
    
    # Add test path
    pytest_args.append(str(test_path))
    
    # Run tests
    return pytest.main(pytest_args)

def main():
    args = parse_args()
    result = run_tests(
        category=args.category,
        coverage=args.coverage,
        verbose=args.verbose
    )
    sys.exit(result)

if __name__ == '__main__':
    main() 