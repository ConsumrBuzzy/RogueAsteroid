"""Integration tests for game systems."""
import pytest
import pygame
from pygame import Surface, Vector2
from typing import Tuple

from src.core.entities.base import Entity
from src.core.components import (
    TransformComponent,
    PhysicsComponent,
    RenderComponent,
    CollisionComponent,
    InputComponent,
    ScreenWrapComponent
)
from src.core.game import Game
from src.core.services import ServiceManager
from src.core.services.state_service import GameState
from src.entities.ship import Ship
from src.entities.asteroid import Asteroid
from src.entities.bullet import Bullet

@pytest.fixture
def mock_game():
    """Create a mock game instance for testing."""
    class MockGame:
        def __init__(self):
            self.screen = Surface((800, 600))
            self.dt = 0.016
            self.services = ServiceManager()
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