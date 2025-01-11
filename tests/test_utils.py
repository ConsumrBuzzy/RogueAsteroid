"""Test utilities and fixtures for RogueAsteroid tests."""
import pygame
import pytest
import numpy as np
from typing import Optional, Dict, Any
from dataclasses import dataclass
from src.core.game_state import GameState
from src.core.entities.base import Entity, Component

@dataclass
class GameConfig:
    """Configuration for mock game instance."""
    width: int = 800
    height: int = 600
    fps: int = 60
    dt: float = 1.0 / 60

class MockGame:
    """Mock game class for testing."""
    def __init__(self, config: Optional[GameConfig] = None):
        self.config = config or GameConfig()
        self.width = self.config.width
        self.height = self.config.height
        self.dt = self.config.dt
        self.state = GameState.PLAYING
        self.entities: list[Entity] = []
        self.screen = pygame.Surface((self.width, self.height))
        self._debug = False
        
    def add_entity(self, entity: Entity) -> None:
        """Add entity to game."""
        self.entities.append(entity)
        
    def remove_entity(self, entity: Entity) -> None:
        """Remove entity from game."""
        if entity in self.entities:
            self.entities.remove(entity)
            
    @property
    def debug(self) -> bool:
        """Get debug state."""
        return self._debug
    
    @debug.setter
    def debug(self, value: bool) -> None:
        """Set debug state."""
        self._debug = value

class MockEntity(Entity):
    """Mock entity for testing."""
    def __init__(self, game: MockGame, **kwargs):
        super().__init__(game)
        self.test_data = kwargs

class MockComponent(Component):
    """Mock component for testing."""
    def __init__(self, entity: Entity, **kwargs):
        super().__init__(entity)
        self.test_data = kwargs
        
    def update(self, dt: float) -> None:
        """Update component."""
        pass

@pytest.fixture
def game_config() -> GameConfig:
    """Fixture for game configuration."""
    return GameConfig()

@pytest.fixture
def mock_game(game_config: GameConfig) -> MockGame:
    """Fixture for mock game instance."""
    return MockGame(game_config)

@pytest.fixture
def mock_entity(mock_game: MockGame) -> MockEntity:
    """Fixture for mock entity."""
    return MockEntity(mock_game)

def create_test_entity(game: MockGame, components: Dict[type, Dict[str, Any]] = None) -> Entity:
    """Create an entity with specified components for testing.
    
    Args:
        game: Game instance
        components: Dictionary mapping component types to their initialization parameters
        
    Returns:
        Entity with specified components
    """
    entity = Entity(game)
    if components:
        for component_type, params in components.items():
            entity.add_component(component_type, **params)
    return entity

class GameStateMixin:
    """Mixin for testing game states."""
    
    @pytest.fixture(autouse=True)
    def setup_game_state(self, mock_game: MockGame):
        """Setup game state for testing."""
        self.game = mock_game
        
    def set_game_state(self, state: GameState):
        """Set game state."""
        self.game.state = state
        
    def assert_game_state(self, expected_state: GameState):
        """Assert game is in expected state."""
        assert self.game.state == expected_state

class EntityTestMixin:
    """Mixin for testing entities."""
    
    @pytest.fixture(autouse=True)
    def setup_entity(self, mock_game: MockGame):
        """Setup entity for testing."""
        self.game = mock_game
        self.entity = create_test_entity(self.game)
        
    def add_component(self, component_type: type, **kwargs) -> Component:
        """Add component to test entity."""
        return self.entity.add_component(component_type, **kwargs)
        
    def assert_has_component(self, component_type: type):
        """Assert entity has component."""
        assert self.entity.has_component(component_type)
        
    def get_component(self, component_type: type) -> Optional[Component]:
        """Get component from test entity."""
        return self.entity.get_component(component_type) 