"""Test configuration for RogueAsteroid."""
import os
import sys
import pytest
import pygame

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@pytest.fixture(scope="session", autouse=True)
def pygame_setup():
    """Initialize pygame for the test session."""
    # Initialize pygame with only the modules we need
    pygame.display.init()
    pygame.font.init()
    
    # Create a dummy display surface
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    
    yield
    
    # Cleanup pygame
    pygame.display.quit()
    pygame.font.quit()
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