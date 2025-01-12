"""Test suite for game state system."""
import pytest
import pygame
from src.core.game_state import GameState
from src.core.game import Game

@pytest.fixture
def game(mock_game, screen):
    """Create a game instance for testing."""
    game = Game()
    game.screen = screen
    yield game

@pytest.mark.game
class TestGameState:
    """Test cases for game state management."""
    
    def test_state_transitions(self, game):
        """Test game state transitions."""
        # Test initial state
        assert game.state_manager.current_state == GameState.MAIN_MENU
        
        # Test playing state
        game.state_manager.change_state(GameState.PLAYING)
        assert game.state_manager.current_state == GameState.PLAYING
        
        # Test pause state
        game.state_manager.change_state(GameState.PAUSED)
        assert game.state_manager.current_state == GameState.PAUSED
        
        # Test resume state
        game.state_manager.change_state(GameState.PLAYING)
        assert game.state_manager.current_state == GameState.PLAYING
        
        # Test game over state
        game.state_manager.change_state(GameState.GAME_OVER)
        assert game.state_manager.current_state == GameState.GAME_OVER
    
    def test_invalid_state_transition(self, game):
        """Test that invalid state transitions are handled."""
        initial_state = game.state_manager.current_state
        # Try to change to same state
        game.state_manager.change_state(initial_state)
        assert game.state_manager.current_state == initial_state
        
        # Try to transition to invalid state
        with pytest.raises(ValueError):
            game.state_manager.change_state("INVALID_STATE")
    
    def test_state_history(self, game):
        """Test that state history is maintained."""
        # Record state transitions
        transitions = [
            GameState.PLAYING,
            GameState.PAUSED,
            GameState.PLAYING,
            GameState.GAME_OVER
        ]
        
        # Execute transitions
        for state in transitions:
            game.state_manager.change_state(state)
            
        # Verify history
        assert game.state_manager.current_state == GameState.GAME_OVER
        assert game.state_manager.previous_state == GameState.PLAYING 