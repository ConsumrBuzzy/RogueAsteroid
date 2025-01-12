"""Tests for ship entity."""
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
    ScreenWrapComponent
)
from src.core.components import ComponentRegistry
from src.core.components.physics import PhysicsComponent
from src.core.services import ServiceManager
from src.entities.ship import Ship

@pytest.fixture
def mock_game():
    """Create a mock game instance for testing."""
    class MockGame:
        def __init__(self):
            self.screen = Surface((800, 600))
            self.width = 800
            self.height = 600
            self.dt = 0.016
            self.services = ServiceManager(self)
            self.component_registry = ComponentRegistry()
    return MockGame()

@pytest.fixture
def ship(mock_game):
    """Create a test ship."""
    return Ship(mock_game)

@pytest.mark.unit
class TestShip:
    """Test cases for Ship entity."""
    
    def test_ship_init(self, ship):
        """Test ship initialization."""
        assert isinstance(ship, Entity)
        assert ship.get_transform() is not None
        assert ship.get_physics() is not None
        assert ship.get_render() is not None
        assert ship.get_collision() is not None
        assert ship.get_input() is not None
        assert ship.get_effects() is not None
    
    def test_ship_thrust(self, ship):
        """Test ship thrust mechanics."""
        transform = ship.get_transform()
        physics = ship.get_physics()
        
        initial_pos = Vector2(transform.position)
        ship._thrust_forward()
        physics.update(0.016)
        assert transform.position != initial_pos
    
    def test_ship_rotation(self, ship):
        """Test ship rotation."""
        transform = ship.get_transform()
        initial_rotation = transform.rotation
        
        ship._rotate_left()
        assert transform.rotation < initial_rotation
        
        initial_rotation = transform.rotation
        ship._rotate_right()
        assert transform.rotation > initial_rotation 