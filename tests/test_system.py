"""Tests for game systems."""
import pytest
import pygame
from pygame import Surface, Vector2
from typing import Tuple

from src.core.services import ServiceManager
from src.core.game import Game
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
from src.core.entities.base import Entity

@pytest.fixture
def mock_game():
    """Create a mock game instance for testing."""
    class MockGame:
        def __init__(self):
            self.screen = Surface((800, 600))
            self.dt = 1.0 / TARGET_FPS
            self.services = ServiceManager(self)
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
        services = ServiceManager(mock_game)
        assert services is not None
        
        # Register a test service
        class TestService:
            def __init__(self, game):
                self.game = game
                self.initialized = True
                
        services.register_service('test', TestService)
        service = services.get_service('test')
        assert service is not None
        assert service.initialized is True
        assert service.game is mock_game
    
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