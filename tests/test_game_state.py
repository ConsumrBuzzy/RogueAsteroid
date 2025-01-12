"""Test suite for game state system."""
import pytest
import pygame
from src.core.game_state import GameState
from src.core.game import Game

@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    """Initialize pygame for all tests."""
    pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    if not pygame.display.get_init():
        pygame.display.init()
    yield
    pygame.quit()

@pytest.fixture
def game():
    """Create a game instance for testing."""
    game = Game()
    yield game
    # Clean up game resources
    if hasattr(game, 'screen'):
        pygame.display.quit()

class TestGameState:
    def test_state_transitions(self, game):
        """Test game state transitions"""
        assert game.state_manager.current_state == GameState.MAIN_MENU
        game.state_manager.change_state(GameState.PLAYING)
        assert game.state_manager.current_state == GameState.PLAYING
        game.state_manager.change_state(GameState.PAUSED)
        assert game.state_manager.current_state == GameState.PAUSED
        game.state_manager.change_state(GameState.PLAYING)
        assert game.state_manager.current_state == GameState.PLAYING
        game.state_manager.change_state(GameState.GAME_OVER)
        assert game.state_manager.current_state == GameState.GAME_OVER
    
    def test_invalid_state_transition(self, game):
        """Test that invalid state transitions are handled."""
        initial_state = game.state_manager.current_state
        # Try to change to same state
        game.state_manager.change_state(initial_state)
        assert game.state_manager.current_state == initial_state
    
    def test_state_history(self, game):
        """Test that state history is maintained."""
        game.state_manager.change_state(GameState.PLAYING)
        game.state_manager.change_state(GameState.PAUSED)
        game.state_manager.change_state(GameState.PLAYING)
        assert game.state_manager.previous_state == GameState.PAUSED 