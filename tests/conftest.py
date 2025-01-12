"""Shared test fixtures and configuration."""
import pytest
import pygame
from src.core.entities.base import Entity, TransformComponent

@pytest.fixture(scope="session", autouse=True)
def pygame_setup():
    """Initialize pygame for all tests."""
    pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    if not pygame.display.get_init():
        pygame.display.init()
    yield
    pygame.quit()

@pytest.fixture
def mock_game():
    """Fixture providing a mock game instance."""
    class MockGame:
        def __init__(self):
            self.width = 800
            self.height = 600
            self.dt = 0.016  # 60 FPS
            self.settings = {
                'controls': {'scheme': 'arrows'},
                'graphics': {'fullscreen': False, 'vsync': True},
                'audio': {'music_volume': 0.7, 'sfx_volume': 1.0}
            }
            self.running = True
            self.paused = False
    return MockGame()

@pytest.fixture
def base_entity(mock_game):
    """Fixture providing a base entity with transform component."""
    entity = Entity(mock_game)
    transform = entity.add_component(TransformComponent)
    transform.position = pygame.Vector2(0.0, 0.0)
    transform.velocity = pygame.Vector2(0.0, 0.0)
    transform.rotation = 0.0
    return entity, transform

@pytest.fixture
def screen():
    """Fixture providing a pygame screen surface."""
    return pygame.Surface((800, 600))

@pytest.fixture
def clock():
    """Fixture providing a pygame clock."""
    return pygame.time.Clock()

@pytest.fixture
def event_queue():
    """Fixture providing an empty event queue."""
    pygame.event.clear()
    return [] 