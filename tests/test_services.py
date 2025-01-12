"""Tests for game services."""
import pytest
from typing import Optional

from src.core.services.service_manager import ServiceManager
from src.core.services.state_service import StateService
from src.core.state.game_states import GameState

# Mock services for testing
class MockService:
    """A basic mock service."""
    def __init__(self):
        self.initialized = True

class MockGameDependentService:
    """A mock service that requires game instance."""
    def __init__(self, game):
        self.game = game
        self.initialized = True

class MockDependentService:
    """A mock service that depends on MockService."""
    def __init__(self, mock_service: MockService):
        self.mock_service = mock_service
        self.initialized = True

@pytest.fixture
def mock_game():
    """Create a mock game instance."""
    class MockGame:
        def __init__(self):
            self.initialized = True
    return MockGame()

@pytest.fixture
def service_manager(mock_game):
    """Create a service manager instance."""
    return ServiceManager(game=mock_game)

@pytest.fixture
def state_service():
    """Create a state service instance."""
    return StateService()

@pytest.mark.unit
class TestServiceManager:
    """Test cases for ServiceManager."""
    
    def test_service_manager_init(self, service_manager):
        """Test service manager initialization."""
        assert service_manager is not None
        assert service_manager.game is not None
        
    def test_register_basic_service(self, service_manager):
        """Test registering a basic service."""
        service_manager.register_service("mock", MockService)
        service = service_manager.get_service(MockService)
        assert service is not None
        assert isinstance(service, MockService)
        assert service.initialized
        
    def test_register_game_dependent_service(self, service_manager):
        """Test registering a service that requires game instance."""
        service_manager.register_service("game_dependent", MockGameDependentService)
        service = service_manager.get_service(MockGameDependentService)
        assert service is not None
        assert isinstance(service, MockGameDependentService)
        assert service.game == service_manager.game
        
    def test_register_dependent_service(self, service_manager):
        """Test registering a service with dependencies."""
        # Register the dependency first
        service_manager.register_service("mock", MockService)
        # Register the dependent service
        service_manager.register_service("dependent", MockDependentService)
        
        service = service_manager.get_service(MockDependentService)
        assert service is not None
        assert isinstance(service, MockDependentService)
        assert isinstance(service.mock_service, MockService)
        
    def test_duplicate_service_registration(self, service_manager):
        """Test that registering a duplicate service raises an error."""
        service_manager.register_service("mock", MockService)
        with pytest.raises(RuntimeError):
            service_manager.register_service("mock", MockService)
            
    def test_cleanup(self, service_manager):
        """Test service cleanup."""
        service_manager.register_service("mock", MockService)
        service_manager.cleanup()
        assert service_manager.get_service(MockService) is None 

@pytest.mark.unit
class TestStateService:
    """Test cases for StateService."""
    
    def test_state_service_init(self, state_service):
        """Test state service initialization."""
        assert state_service is not None
        assert state_service.is_ready()
        assert state_service.get_current_state() == GameState.MAIN_MENU
        
    def test_state_transitions(self, state_service):
        """Test state transitions."""
        # Test valid transitions
        state_service.change_state(GameState.PLAYING)
        assert state_service.get_current_state() == GameState.PLAYING
        
        state_service.change_state(GameState.PAUSED)
        assert state_service.get_current_state() == GameState.PAUSED
        assert state_service.get_previous_state() == GameState.PLAYING
        
    def test_invalid_state_transition(self, state_service):
        """Test that invalid state transitions raise an error."""
        # Can't go directly from MAIN_MENU to GAME_OVER
        with pytest.raises(ValueError):
            state_service.change_state(GameState.GAME_OVER)
            
    def test_state_handlers(self, state_service):
        """Test state handler registration and execution."""
        handler_called = False
        
        class TestHandler:
            def __init__(self):
                self.called = False
                
            def __call__(self):
                """Make the handler callable."""
                pass
                
            def on_enter(self):
                self.called = True
                
            def on_exit(self):
                pass
                
        handler = TestHandler()
        state_service.register_handler(GameState.PLAYING, handler)
        state_service.change_state(GameState.PLAYING)
        assert handler.called
        
    def test_state_service_singleton(self):
        """Test that StateService is a singleton."""
        service1 = StateService()
        service2 = StateService()
        assert service1 is service2 