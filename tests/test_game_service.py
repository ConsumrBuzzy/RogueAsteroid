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
        self.update = MagicMock()
        
    def _change_state(self, new_state):
        """Change the current state."""
        self.current_state = new_state

class MockEventManager:
    def __init__(self):
        self.subscribe = MagicMock()
        self.publish = MagicMock()
        self.process_events = MagicMock()

class MockResourceManager:
    def __init__(self):
        self.preload_resources = MagicMock()
        self.update = MagicMock()

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
        self.update = MagicMock()

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
        self.update = MagicMock()

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
        
    def test_spawn_player_ship(self, game_service):
        """Test player ship spawning."""
        # Mock the ship creation
        mock_ship = MagicMock()
        mock_transform = MagicMock()
        mock_ship.get_component.return_value = mock_transform
        mock_transform.position = pygame.Vector2(400, 300)
        game_service._entity_factory.create_ship.return_value = mock_ship
        
        # Trigger game start to spawn ship
        game_service.start()
        
        # Verify ship was created and registered
        game_service._entity_factory.create_ship.assert_called_once()
        assert game_service.player_ship == mock_ship
        assert mock_ship in game_service.entities
        game_service._physics_service.register_entity.assert_called_with(mock_ship)
        game_service._collision_service.register_entity.assert_called_with(mock_ship)
        game_service._render_service.add_to_layer.assert_called_with('game', mock_ship)
        
    def test_spawn_asteroids(self, game_service, monkeypatch):
        """Test asteroid spawning."""
        # Mock the ship and asteroid creation
        mock_ship = MagicMock()
        mock_ship.get_component.return_value = MagicMock(position=pygame.Vector2(400, 300))
        game_service.player_ship = mock_ship
        
        # Mock the Asteroid class
        class MockAsteroid:
            def __init__(self, size="large", position=None, ship_pos=None):
                self.size = size
                self.position = position
                self.ship_pos = ship_pos
                
        monkeypatch.setattr("src.entities.asteroid.Asteroid", MockAsteroid)
        
        # Spawn asteroids
        count = 3
        game_service._spawn_asteroids(count)
        
        # Verify asteroids were created and registered
        assert len(game_service.asteroids) == count
        assert isinstance(game_service.asteroids[0], MockAsteroid)
        assert game_service._physics_service.register_entity.call_count >= count
        assert game_service._collision_service.register_entity.call_count >= count
        
    def test_game_over(self, game_service):
        """Test game over handling."""
        # Setup initial game state
        game_service.start()
        game_service._score = 1000
        
        # Trigger game over
        game_service._on_game_over(score=game_service._score)
        
        # Verify game over state
        assert game_service._state_service.get_current_state() == GameState.GAME_OVER
        game_service._high_score_service.add_score.assert_called_with(1000)
        
    def test_level_complete(self, game_service, monkeypatch):
        """Test level completion handling."""
        # Setup initial game state
        initial_level = game_service._level
        
        # Mock player ship for asteroid spawning
        mock_ship = MagicMock()
        mock_ship.get_component.return_value = MagicMock(position=pygame.Vector2(400, 300))
        game_service.player_ship = mock_ship
        
        # Mock the Asteroid class
        class MockAsteroid:
            def __init__(self, size="large", position=None, ship_pos=None):
                self.size = size
                self.position = position
                self.ship_pos = ship_pos
                
        monkeypatch.setattr("src.entities.asteroid.Asteroid", MockAsteroid)
        
        # Trigger level complete
        game_service._on_level_complete(level=initial_level)
        
        # Verify level progression
        assert game_service._level == initial_level + 1
        assert len(game_service.asteroids) > 0
        
    def test_update_game_state(self, game_service):
        """Test game state updates."""
        # Start the game
        game_service.start()
        game_service._state_service.current_state = GameState.PLAYING
        game_service._paused = False
        
        # Update game state
        dt = 0.016  # 60 FPS
        game_service.update(dt)
        
        # Verify services were updated
        game_service._input_service.update.assert_called_once()
        game_service._physics_service.update.assert_called_with(dt)
        game_service._collision_service.update.assert_called_once()
        game_service._particle_service.update.assert_called_with(dt)
        game_service._state_service.update.assert_called_with(dt)
        game_service._menu_service.update.assert_called_with(dt)
        
    def test_draw_game_state(self, game_service):
        """Test game rendering."""
        # Start the game
        game_service.start()
        
        # Draw game state
        game_service.draw()
        
        # Verify rendering services were called
        game_service._render_service.draw.assert_called_once()
        game_service._particle_service.draw.assert_called_once()
        game_service._ui_service.draw.assert_called_once() 