"""Tests for game systems."""
import pytest
import pygame
from pygame import Surface, Vector2
from typing import Tuple

from src.core.services import ServiceManager
from src.core.services.state_service import GameState
from src.core.components.base import (
    TransformComponent,
    RenderComponent,
    CollisionComponent,
    InputComponent,
    ScreenWrapComponent
)
from src.core.components.physics import PhysicsComponent
from src.core.components import ComponentRegistry
from src.core.game import Game
from src.entities.ship import Ship
from src.entities.asteroid import Asteroid
from src.entities.bullet import Bullet
from src.core.config.entities import (
    SHIP_ACCELERATION,
    SHIP_ROTATION_SPEED,
    SHIP_MAX_SPEED,
    ASTEROID_SIZES,
    BULLET_SPEED,
    BULLET_LIFETIME
)
from src.core.config.gameplay import (
    INITIAL_ASTEROIDS,
    ASTEROIDS_INCREMENT,
    MAX_ASTEROIDS
)
from src.core.config.display import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT
)

@pytest.fixture
def mock_game():
    """Create a mock game instance for testing."""
    class MockGame:
        def __init__(self):
            self.screen = Surface((800, 600))
            self.dt = 0.016
            self.services = ServiceManager(self)
            self.component_registry = ComponentRegistry()
    return MockGame()

@pytest.fixture
def entity(mock_game):
    """Create a test entity."""
    return Entity(mock_game)

@pytest.mark.integration
class TestGameIntegration:
    """Integration tests for game systems."""
    
    def test_game_initialization(self, mock_game):
        """Test game initialization."""
        game = Game()
        assert game.services is not None
        assert game.screen is not None
        assert game.running is True
    
    def test_entity_creation(self, mock_game):
        """Test entity creation and management."""
        game = Game()
        ship = Ship(game)
        assert ship in game.services.get_service('entity_manager').entities
        
        asteroid = Asteroid(game, 'large', Vector2(400, 300))
        assert asteroid in game.services.get_service('entity_manager').entities 