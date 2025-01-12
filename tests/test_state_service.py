"""Tests for StateService."""
import pytest
from src.core.services.state_service import StateService
from src.core.state.game_states import GameState

@pytest.fixture
def state_service():
    """Create a state service instance."""
    return StateService()

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