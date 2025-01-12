"""Tests for game entities."""
import pytest
import pygame
from pygame import Surface, Vector2
from typing import Tuple

from src.core.entities.base import Entity
from src.core.components.base import (
    TransformComponent,
    RenderComponent,
    CollisionComponent,
    InputComponent,
    ScreenWrapComponent,
    ComponentRegistry
)
from src.core.components.physics import PhysicsComponent
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

@pytest.fixture
def mock_game():
    """Create a mock game instance for testing."""
    class MockGame:
        def __init__(self):
            self.screen = Surface((800, 600))
            self.dt = 0.016
    return MockGame()

@pytest.fixture
def entity(mock_game):
    """Create a test entity."""
    return Entity(mock_game)

@pytest.mark.unit
class TestShip:
    """Test cases for Ship entity."""
    
    def test_ship_init(self, mock_game):
        """Test ship initialization."""
        ship = Ship(mock_game)
        assert isinstance(ship, Entity)
        assert ship.get_component(TransformComponent) is not None
        assert ship.get_component(PhysicsComponent) is not None
        assert ship.get_component(RenderComponent) is not None
        assert ship.get_component(CollisionComponent) is not None
        assert ship.get_component(InputComponent) is not None
        assert ship.get_component(ScreenWrapComponent) is not None
    
    def test_ship_movement(self, mock_game):
        """Test ship movement."""
        ship = Ship(mock_game)
        transform = ship.get_component(TransformComponent)
        physics = ship.get_component(PhysicsComponent)
        
        initial_pos = Vector2(transform.position)
        ship.thrust(1.0)
        physics.update(0.016)
        assert transform.position != initial_pos 