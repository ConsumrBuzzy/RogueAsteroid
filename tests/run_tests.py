#!/usr/bin/env python3
"""Test runner for RogueAsteroid test suites."""
import pytest
import sys
import os
import pygame

def init_pygame():
    """Initialize pygame and its subsystems."""
    try:
        pygame.init()
        if pygame.get_init():
            print("Pygame initialized successfully")
            # Initialize required subsystems
            if not pygame.font.get_init():
                pygame.font.init()
            if not pygame.display.get_init():
                pygame.display.init()
            return True
        return False
    except Exception as e:
        print(f"Error initializing pygame: {e}", file=sys.stderr)
        return False

def run_tests():
    """Run all test suites with coverage reporting."""
    # Add source directory to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Initialize pygame first
    if not init_pygame():
        print("Failed to initialize pygame")
        return 1
    
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
    
    try:
        # Run tests
        result = pytest.main(pytest_args)
        return result
    finally:
        # Clean up pygame
        pygame.quit()

if __name__ == '__main__':
    print("Running RogueAsteroid Test Suite")
    print("-" * 40)
    
    # Run tests and get exit code
    exit_code = run_tests()
    
    # Exit with test result
    sys.exit(exit_code) 