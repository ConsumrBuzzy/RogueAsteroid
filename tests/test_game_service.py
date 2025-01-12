"""Tests for GameService."""
import pytest
import pygame
from typing import Dict, Optional
from unittest.mock import MagicMock

from src.core.services.game_service import GameService
from src.core.services.service_manager import ServiceManager
from src.core.state.game_states import GameState

# Mock services
class MockStateService:
    """Mock state service for testing."""
    def __init__(self):
        self.current_state = GameState.MAIN_MENU
        self.is_ready = lambda: True
        self.change_state = self._change_state
        self.get_current_state = lambda: self.current_state
        
    def _change_state(self, new_state):
        """Change the current state."""
        self.current_state = new_state

class MockEventManager:
    def __init__(self):
        self.subscribe = MagicMock()
        self.publish = MagicMock()

class MockResourceManager:
    def __init__(self):
        self.preload_resources = MagicMock()

class MockPhysicsService:
    def __init__(self):
        self.update = MagicMock()
        self.clear = MagicMock()
        self.register_entity = MagicMock()
        self.unregister_entity = MagicMock()

class MockRenderService:
    def __init__(self):
        self.draw = MagicMock()
        self.clear = MagicMock()
        self.add_to_layer = MagicMock()
        self.remove_from_layer = MagicMock()

class MockCollisionService:
    def __init__(self):
        self.update = MagicMock()
        self.clear = MagicMock()
        self.register_entity = MagicMock()
        self.unregister_entity = MagicMock()

class MockParticleService:
    def __init__(self):
        self.update = MagicMock()
        self.draw = MagicMock()
        self.clear = MagicMock()

class MockUIService:
    def __init__(self):
        self.update = MagicMock()
        self.draw = MagicMock()
        self.clear = MagicMock()

class MockMenuService:
    def __init__(self):
        self.update = MagicMock()

class MockInputService:
    def __init__(self):
        self.update = MagicMock()

class MockHighScoreService:
    def __init__(self):
        self.add_score = MagicMock()

class MockAchievementService:
    def __init__(self):
        self.update = MagicMock()

class MockStatisticsService:
    def __init__(self):
        self.update = MagicMock()

class MockEntityFactory:
    def __init__(self):
        self.create_ship = MagicMock()
        self.create_asteroid = MagicMock()

@pytest.fixture
def mock_screen():
    """Create a mock pygame screen."""
    return pygame.Surface((800, 600))

@pytest.fixture
def mock_settings():
    """Create mock game settings."""
    return {
        'window_width': 800,
        'window_height': 600,
        'fps': 60,
        'debug': False
    }

@pytest.fixture
def service_manager():
    """Create a service manager with mock services."""
    manager = ServiceManager()
    
    # Register all mock services
    manager.register_service('state', MockStateService)
    manager.register_service('events', MockEventManager)
    manager.register_service('resources', MockResourceManager)
    manager.register_service('physics', MockPhysicsService)
    manager.register_service('render', MockRenderService)
    manager.register_service('collision', MockCollisionService)
    manager.register_service('particle', MockParticleService)
    manager.register_service('ui', MockUIService)
    manager.register_service('menu', MockMenuService)
    manager.register_service('input', MockInputService)
    manager.register_service('high_score', MockHighScoreService)
    manager.register_service('achievement', MockAchievementService)
    manager.register_service('statistics', MockStatisticsService)
    manager.register_service('entity_factory', MockEntityFactory)
    
    return manager

@pytest.fixture
def game_service(mock_screen, mock_settings, service_manager):
    """Create a game service instance with mock dependencies."""
    return GameService(mock_screen, mock_settings, service_manager)

@pytest.mark.unit
class TestGameService:
    """Test cases for GameService."""
    
    def test_game_service_init(self, game_service):
        """Test game service initialization."""
        assert game_service is not None
        assert game_service.width == 800
        assert game_service.height == 600
        assert not game_service.is_running()
        assert not game_service.is_paused()
        
    def test_game_start_stop(self, game_service):
        """Test game start and stop."""
        game_service.start()
        assert game_service.is_running()
        
        game_service.stop()
        assert not game_service.is_running()
        
    def test_game_pause_resume(self, game_service):
        """Test game pause and resume."""
        # Start the game and ensure we're in PLAYING state
        game_service.start()
        game_service._state_service.current_state = GameState.PLAYING
        
        # Test pause
        game_service.pause()
        assert game_service.is_paused()
        assert game_service._state_service.get_current_state() == GameState.PAUSED
        
        # Test resume
        game_service.resume()
        assert not game_service.is_paused()
        assert game_service._state_service.get_current_state() == GameState.PLAYING
        
    def test_game_clear(self, game_service):
        """Test game state clearing."""
        game_service.clear()
        
        # Verify all services were cleared
        game_service._render_service.clear.assert_called_once()
        game_service._physics_service.clear.assert_called_once()
        game_service._collision_service.clear.assert_called_once()
        game_service._particle_service.clear.assert_called_once()
        game_service._ui_service.clear.assert_called_once()
        
        assert len(game_service.entities) == 0
        assert len(game_service.asteroids) == 0
        assert len(game_service.bullets) == 0
        assert game_service.player_ship is None 