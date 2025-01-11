"""Test configuration for RogueAsteroid."""
import os
import sys
import pytest
import pygame

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Initialize pygame for tests
pygame.init()

@pytest.fixture(autouse=True)
def cleanup_pygame():
    """Cleanup pygame after each test."""
    yield
    pygame.quit()

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment."""
    # Create any necessary test directories
    os.makedirs(os.path.join(project_root, "tests", "coverage"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "tests", "data"), exist_ok=True)
    
    yield
    
    # Cleanup any test artifacts if needed
    pass 