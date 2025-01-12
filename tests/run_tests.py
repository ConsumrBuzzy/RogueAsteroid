#!/usr/bin/env python3
"""Test runner for RogueAsteroid game."""
import sys
import os
import pytest
import pygame

def init_pygame():
    """Initialize pygame and required subsystems."""
    try:
        pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
        if not pygame.display.get_init():
            pygame.display.init()
        print("Pygame initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing pygame: {e}")
        return False

def run_tests():
    """Run all test suites."""
    try:
        # Initialize pygame first
        if not init_pygame():
            print("Failed to initialize pygame, aborting tests")
            return False
            
        # Add src directory to Python path
        src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
            
        # Run test suites
        test_files = [
            'test_game_state.py',
            'test_scoring.py',
            'test_particles.py',
            'test_menu.py',
            'test_collision.py'
        ]
        
        args = [
            '-v',  # Verbose output
            '--tb=short',  # Shorter traceback format
            '--capture=no'  # Show print statements
        ]
        
        # Add test files to args
        args.extend([os.path.join('tests', f) for f in test_files])
        
        # Run pytest
        result = pytest.main(args)
        
        # Clean up pygame
        pygame.quit()
        
        return result == 0
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return False
    finally:
        # Ensure pygame is quit even if there's an error
        pygame.quit()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1) 