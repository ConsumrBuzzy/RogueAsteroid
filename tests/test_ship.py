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
        assert ship.get_component(TransformComponent) is not None
        assert ship.get_component(PhysicsComponent) is not None
        assert ship.get_component(RenderComponent) is not None
        assert ship.get_component(CollisionComponent) is not None
        assert ship.get_component(InputComponent) is not None
        assert ship.get_component(ScreenWrapComponent) is not None
    
    def test_ship_thrust(self, ship):
        """Test ship thrust mechanics."""
        transform = ship.get_component(TransformComponent)
        physics = ship.get_component(PhysicsComponent)
        
        initial_pos = Vector2(transform.position)
        ship.thrust(1.0)
        physics.update(0.016)
        assert transform.position != initial_pos
    
    def test_ship_rotation(self, ship):
        """Test ship rotation."""
        transform = ship.get_component(TransformComponent)
        initial_rotation = transform.rotation
        
        ship.rotate_left(1.0)
        assert transform.rotation < initial_rotation
        
        initial_rotation = transform.rotation
        ship.rotate_right(1.0)
        assert transform.rotation > initial_rotation 