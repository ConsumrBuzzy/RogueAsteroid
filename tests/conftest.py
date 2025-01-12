"""Test fixtures and configuration for RogueAsteroid tests."""
import os
import sys
import pytest
import pygame
from typing import Generator, Any

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.core.components.base import (
    Component,
    TransformComponent,
    RenderComponent,
    CollisionComponent,
    InputComponent,
    ScreenWrapComponent
)
from src.core.entities.base import Entity
from src.core.components import ComponentRegistry
from src.core.services import ServiceManager

class MockGame:
    """Mock game class for testing."""
    def __init__(self):
        self.screen = pygame.Surface((800, 600))
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 1.0 / 60.0
        self.services = ServiceManager()

@pytest.fixture(scope="session", autouse=True)
def pygame_init() -> Generator[None, None, None]:
    """Initialize pygame for tests that need it."""
    pygame.init()
    yield
    pygame.quit()

@pytest.fixture
def screen() -> pygame.Surface:
    """Create a test screen surface."""
    return pygame.Surface((800, 600))

@pytest.fixture
def mock_game() -> MockGame:
    """Create a mock game instance for testing."""
    return MockGame()

@pytest.fixture
def entity(mock_game: MockGame) -> Entity:
    """Create a basic test entity."""
    return Entity(mock_game)

@pytest.fixture
def transform(entity: Entity) -> TransformComponent:
    """Create a transform component for testing."""
    return entity.add_component('TransformComponent', x=400, y=300)

@pytest.fixture
def render(entity: Entity) -> RenderComponent:
    """Create a render component for testing."""
    points = [(0, -10), (-5, 5), (5, 5)]  # Triangle shape
    return entity.add_component('RenderComponent', color=(255, 255, 255), points=points)

@pytest.fixture
def collision(entity: Entity) -> CollisionComponent:
    """Create a collision component for testing."""
    return entity.add_component('CollisionComponent', radius=10)

@pytest.fixture
def input_component(entity: Entity) -> InputComponent:
    """Create an input component for testing."""
    return entity.add_component('InputComponent')

@pytest.fixture
def screen_wrap(entity: Entity) -> ScreenWrapComponent:
    """Create a screen wrap component for testing."""
    return entity.add_component('ScreenWrapComponent')

@pytest.fixture
def component_registry() -> ComponentRegistry:
    """Get the component registry instance."""
    return ComponentRegistry()

@pytest.fixture
def mock_dt() -> float:
    """Return a mock delta time value."""
    return 1.0 / 60.0  # 60 FPS

@pytest.fixture
def mock_event() -> pygame.event.Event:
    """Create a mock pygame event."""
    return pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE})

class PerformanceEnv:
    """Environment for performance testing."""
    def __init__(self):
        self.screen = pygame.Surface((800, 600))
        self.dt = 1/60
        self.running = True
        self.position = (400, 300)  # Center position for testing

@pytest.fixture
def performance_env() -> PerformanceEnv:
    """Create a performance testing environment."""
    return PerformanceEnv()

@pytest.fixture
def test_entity(mock_game) -> Entity:
    """Create a test entity for performance testing."""
    return Entity(mock_game) 