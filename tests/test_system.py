"""Tests for game systems."""
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
from src.core.constants import TARGET_FPS

@pytest.fixture
def mock_game():
    """Create a mock game instance for testing."""
    class MockGame:
        def __init__(self):
            self.screen = Surface((800, 600))
            self.dt = 1.0 / TARGET_FPS
            self.services = ServiceManager()
    return MockGame()

@pytest.fixture
def entity(mock_game):
    """Create a test entity."""
    return Entity(mock_game)

@pytest.mark.system
class TestGameSystems:
    """Test cases for game systems."""
    
    def test_service_manager(self, mock_game):
        """Test service manager initialization and registration."""
        services = ServiceManager()
        assert services is not None
        
        # Register a test service
        class TestService:
            def __init__(self, game):
                self.game = game
                
        services.register_service('test', TestService(mock_game))
        assert services.get_service('test') is not None
    
    def test_game_loop(self, mock_game):
        """Test game loop timing."""
        game = Game()
        start_time = pygame.time.get_ticks()
        
        # Run for 10 frames
        for _ in range(10):
            game.update(1.0 / TARGET_FPS)
            
        end_time = pygame.time.get_ticks()
        frame_time = (end_time - start_time) / 10
        
        # Frame time should be close to target
        target_frame_time = 1000 / TARGET_FPS  # Convert to milliseconds
        assert abs(frame_time - target_frame_time) < target_frame_time * 0.1 