#!/usr/bin/env python3
"""Test runner for RogueAsteroid test suites."""
import pytest
import sys
import os

def run_tests():
    """Run all test suites with coverage reporting."""
    # Add source directory to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Configure pytest arguments
    pytest_args = [
        '--verbose',
        '--cov=src',
        '--cov-report=term-missing',
        '--cov-report=html:tests/coverage',
        'tests/test_systems.py',  # Core systems tests
        'tests/test_integration.py',  # Integration tests
        'tests/test_entities.py',  # Entity tests
        'tests/test_components.py',  # Component tests
    ]
    
    # Run tests
    return pytest.main(pytest_args)

if __name__ == '__main__':
    print("Running RogueAsteroid Test Suite")
    print("-" * 40)
    
    # Initialize pygame for tests
    import pygame
    pygame.init()
    
    # Run tests and get exit code
    exit_code = run_tests()
    
    # Quit pygame
    pygame.quit()
    
    # Exit with test result
    sys.exit(exit_code) 