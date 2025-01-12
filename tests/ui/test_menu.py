"""Test suite for menu system."""
import pytest
import pygame
from src.core.game import Game
from src.core.game_state import GameState
from src.core.constants import *

@pytest.fixture
def game(mock_game, screen):
    """Create a game instance for testing."""
    game = Game()
    game.screen = screen
    yield game

@pytest.fixture
def menu_setup(game):
    """Setup a fresh game state for menu testing."""
    game.return_to_menu()  # Ensure we're in menu state
    return game

@pytest.mark.ui
class TestMenuSystem:
    """Test cases for the menu system."""
    
    def test_menu_state_transitions(self, game, menu_setup):
        """Test menu state transitions."""
        # Verify initial state
        assert game.state_manager.current_state == GameState.MAIN_MENU, "Should start in main menu"
        
        # Test game start
        game.new_game()
        assert game.state_manager.current_state == GameState.PLAYING, "Should transition to playing state"
        
        # Test pause menu
        game.pause()
        assert game.state_manager.current_state == GameState.PAUSED, "Should transition to paused state"
        
        # Test resume
        game.resume()
        assert game.state_manager.current_state == GameState.PLAYING, "Should return to playing state"
        
        # Test return to menu
        game.return_to_menu()
        assert game.state_manager.current_state == GameState.MAIN_MENU, "Should return to main menu"
    
    def test_menu_input_handling(self, game, menu_setup):
        """Test menu input handling."""
        # Setup mock input handler
        input_events = []
        def mock_handler(event):
            input_events.append(event)
        
        game.menu.add_input_handler(mock_handler)
        
        # Test menu navigation inputs
        test_events = [
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_UP}),
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_DOWN}),
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN})
        ]
        
        for event in test_events:
            game.menu.handle_input(event)
        
        assert len(input_events) == len(test_events), "Menu should handle all input events"
    
    def test_menu_item_selection(self, game, menu_setup):
        """Test menu item selection and highlighting."""
        menu = game.menu
        
        # Get initial selection
        initial_index = menu.selected_index
        
        # Test moving down
        menu.move_selection(1)
        assert menu.selected_index == (initial_index + 1) % len(menu.items), \
            "Selection should move down"
        
        # Test moving up
        menu.move_selection(-1)
        assert menu.selected_index == initial_index, \
            "Selection should move up"
        
        # Test wrapping around
        for _ in range(len(menu.items)):
            menu.move_selection(1)
        assert menu.selected_index == initial_index, \
            "Selection should wrap around"
    
    def test_menu_rendering(self, game, menu_setup):
        """Test menu rendering."""
        menu = game.menu
        
        # Verify menu surface creation
        surface = menu.render()
        assert isinstance(surface, pygame.Surface), "Menu should render to a surface"
        assert surface.get_width() > 0, "Menu surface should have width"
        assert surface.get_height() > 0, "Menu surface should have height"
        
        # Verify all items are rendered
        rendered_items = menu.get_rendered_items()
        assert len(rendered_items) == len(menu.items), "All menu items should be rendered"
        
        # Verify selected item is highlighted
        selected_item = rendered_items[menu.selected_index]
        assert selected_item.color != menu.default_color, "Selected item should be highlighted"
    
    def test_settings_menu(self, game, menu_setup):
        """Test settings menu functionality."""
        # Navigate to settings
        game.menu.open_settings()
        assert game.state_manager.current_state == GameState.SETTINGS, \
            "Should transition to settings state"
        
        # Test settings changes
        initial_volume = game.settings['audio']['music_volume']
        game.menu.change_setting('music_volume', initial_volume + 0.1)
        assert game.settings['audio']['music_volume'] > initial_volume, \
            "Should be able to change settings"
        
        # Test settings persistence
        game.menu.save_settings()
        game.return_to_menu()
        game.menu.open_settings()
        assert game.settings['audio']['music_volume'] > initial_volume, \
            "Settings should persist"
    
    def test_high_score_menu(self, game, menu_setup):
        """Test high score menu functionality."""
        # Add some test scores
        test_scores = [
            ("TEST1", 1000, 1),
            ("TEST2", 2000, 2),
            ("TEST3", 3000, 3)
        ]
        
        for name, score, level in test_scores:
            game.scoring.add_high_score(name, score, level)
        
        # Open high score menu
        game.menu.show_high_scores()
        assert game.state_manager.current_state == GameState.HIGH_SCORES, \
            "Should transition to high scores state"
        
        # Verify scores are displayed
        displayed_scores = game.menu.get_displayed_scores()
        assert len(displayed_scores) == len(test_scores), \
            "Should display all high scores"
        
        # Verify score ordering
        scores = [score for _, score, _ in displayed_scores]
        assert scores == sorted(scores, reverse=True), \
            "Scores should be ordered highest to lowest"
    
    def test_menu_animation(self, game, menu_setup):
        """Test menu animation effects."""
        menu = game.menu
        
        # Test menu item hover animation
        initial_scale = menu.items[0].scale
        menu.update_animations(1/60)  # One frame
        
        selected_item = menu.items[menu.selected_index]
        assert selected_item.scale != initial_scale, \
            "Selected item should animate"
        
        # Test menu transition animation
        initial_alpha = menu.background_alpha
        game.new_game()  # Trigger transition
        menu.update_animations(1/60)
        
        assert menu.background_alpha != initial_alpha, \
            "Menu should animate during transitions" 