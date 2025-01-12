"""Test configuration for RogueAsteroid."""
import os
import sys
import pytest
import pygame
import gc

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@pytest.fixture(scope="session", autouse=True)
def pygame_setup():
    """Initialize pygame for the test session."""
    # Initialize pygame with only the modules we need
    pygame.init()
    pygame.display.init()
    pygame.font.init()
    
    # Create a dummy display surface in memory
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.display.set_mode((800, 600), pygame.NOFRAME)
    
    yield
    
    # Cleanup pygame
    pygame.display.quit()
    pygame.font.quit()
    pygame.quit()

@pytest.fixture(scope="function")
def game_env():
    """Create a clean game environment for each test."""
    from src.core.entity import Entity
    
    class MockGame:
        """Mock game class for testing."""
        def __init__(self):
            self.screen = pygame.Surface((800, 600))
            self.width = 800
            self.height = 600
            self.entities = []
            
        def add_entity(self, entity):
            """Add entity to game."""
            self.entities.append(entity)
            
        def remove_entity(self, entity):
            """Remove entity from game."""
            if entity in self.entities:
                self.entities.remove(entity)
    
    # Create game environment
    game = MockGame()
    
    yield game
    
    # Cleanup
    game.entities.clear()
    gc.collect()

@pytest.fixture(scope="function")
def test_entity(game_env):
    """Create a test entity with basic components."""
    from src.core.entity import Entity
    
    entity = Entity(game_env)
    game_env.add_entity(entity)
    
    yield entity
    
    # Cleanup
    game_env.remove_entity(entity)
    gc.collect()

@pytest.fixture(scope="function")
def performance_env(game_env):
    """Set up environment for performance testing."""
    # Force a garbage collection before performance tests
    gc.collect()
    
    # Disable garbage collection during tests
    gc.disable()
    
    yield game_env
    
    # Re-enable and run garbage collection after test
    gc.enable()
    gc.collect() 