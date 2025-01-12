"""Tests for utility functions."""
import pytest
import pygame
from pygame import Surface, Vector2
from typing import Tuple
from dataclasses import dataclass

from src.core.entities.base import Entity
from src.core.services.state_service import GameState
from src.core.components import (
    TransformComponent,
    PhysicsComponent,
    RenderComponent,
    CollisionComponent,
    InputComponent,
    ScreenWrapComponent
)
from src.core.config.display import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    TARGET_FPS
)
from src.core.config.gameplay import (
    INITIAL_ASTEROIDS,
    ASTEROIDS_INCREMENT,
    MAX_ASTEROIDS,
    PHYSICS_TIME_STEP
)
from src.core.game import Game
from src.core.services import ServiceManager

@dataclass
class MockComponent:
    """Mock component for testing."""
    entity: Entity
    active: bool = True

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

@pytest.mark.unit
class TestUtils:
    """Test cases for utility functions."""
    
    def test_vector_operations(self):
        """Test vector math utilities."""
        v1 = Vector2(3, 4)
        v2 = Vector2(1, 2)
        
        # Addition
        result = v1 + v2
        assert result == Vector2(4, 6)
        
        # Subtraction
        result = v1 - v2
        assert result == Vector2(2, 2)
        
        # Scalar multiplication
        result = v1 * 2
        assert result == Vector2(6, 8)
        
        # Length
        assert abs(v1.length() - 5.0) < 0.0001
    
    def test_component_lifecycle(self, entity):
        """Test component lifecycle utilities."""
        component = MockComponent(entity)
        assert component.active is True
        
        # Deactivate
        component.active = False
        assert component.active is False
        
        # Reactivate
        component.active = True
        assert component.active is True 