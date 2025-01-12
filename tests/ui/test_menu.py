"""Test suite for menu system."""
import pytest
import pygame
from src.core.game import Game
from src.core.game_state import GameState

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

class TestMenu:
    def test_menu_navigation(self, game):
        """Test menu navigation"""
        # Should start in main menu
        assert game.state_manager.current_state == GameState.MAIN_MENU
        
        # Start game
        game.new_game()
        assert game.state_manager.current_state == GameState.PLAYING
        
        # Pause game
        game.pause()
        assert game.state_manager.current_state == GameState.PAUSED
        
        # Resume game
        game.resume()
        assert game.state_manager.current_state == GameState.PLAYING
        
        # Return to menu
        game.return_to_menu()
        assert game.state_manager.current_state == GameState.MAIN_MENU
    
    def test_settings(self, game):
        """Test settings functionality"""
        # Test control scheme setting
        initial_scheme = game.settings['controls']
        game.toggle_control_scheme()
        assert game.settings['controls'] != initial_scheme
        
        # Toggle back
        game.toggle_control_scheme()
        assert game.settings['controls'] == initial_scheme
    
    def test_menu_input(self, game):
        """Test menu input handling."""
        # Start in main menu
        assert game.state_manager.current_state == GameState.MAIN_MENU
        
        # Simulate menu selection
        game.handle_input(pygame.K_RETURN)  # Enter key should start game
        assert game.state_manager.current_state == GameState.PLAYING
        
        # Test pause menu
        game.handle_input(pygame.K_ESCAPE)  # Escape key should pause
        assert game.state_manager.current_state == GameState.PAUSED
        
        # Test resume
        game.handle_input(pygame.K_ESCAPE)  # Escape key should resume
        assert game.state_manager.current_state == GameState.PLAYING
    
    def test_menu_rendering(self, game):
        """Test menu rendering."""
        # Menu should have render method
        assert hasattr(game, 'render')
        
        # Menu should render without errors in different states
        game.state_manager.change_state(GameState.MAIN_MENU)
        game.render()
        
        game.state_manager.change_state(GameState.PAUSED)
        game.render()
        
        game.state_manager.change_state(GameState.GAME_OVER)
        game.render()
    
    def test_menu_state_persistence(self, game):
        """Test that menu state persists correctly."""
        # Change settings
        initial_scheme = game.settings['controls']
        game.toggle_control_scheme()
        
        # Start and quit game
        game.new_game()
        game.return_to_menu()
        
        # Settings should persist
        assert game.settings['controls'] != initial_scheme 