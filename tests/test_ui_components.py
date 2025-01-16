"""Test suite for UI components."""
import pytest
import pygame
from src.core.game_state import StateManager, GameState
from src.core.game import Game

@pytest.fixture
def game():
    """Fixture to create a game instance."""
    return Game()

@pytest.fixture
def state_manager(game):
    """Fixture to create a state manager instance."""
    return StateManager(game)

@pytest.fixture
def pygame_init():
    """Fixture to initialize pygame for UI tests."""
    pygame.init()
    yield
    pygame.quit()

class TestStateManager:
    def test_state_transitions(self, state_manager):
        """Test game state transitions."""
        # Initial state should be None
        assert state_manager.current_state is None
        
        # Test transition to MAIN_MENU
        state_manager.change_state(GameState.MAIN_MENU)
        assert state_manager.current_state == GameState.MAIN_MENU
        
        # Test transition to PLAYING
        state_manager.change_state(GameState.PLAYING)
        assert state_manager.current_state == GameState.PLAYING
        
        # Test transition to PAUSED
        state_manager.change_state(GameState.PAUSED)
        assert state_manager.current_state == GameState.PAUSED
        
        # Test transition back to PLAYING
        state_manager.change_state(GameState.PLAYING)
        assert state_manager.current_state == GameState.PLAYING
        
        # Test transition to GAME_OVER
        state_manager.change_state(GameState.GAME_OVER)
        assert state_manager.current_state == GameState.GAME_OVER

    def test_menu_navigation(self, state_manager):
        """Test menu option navigation."""
        # Set initial state to MAIN_MENU
        state_manager.change_state(GameState.MAIN_MENU)
        assert state_manager.current_state == GameState.MAIN_MENU
        
        # Test moving down in menu
        initial_option = state_manager.selected_option
        state_manager.select_next_option()
        assert state_manager.selected_option == (initial_option + 1) % len(state_manager.menu_options)
        
        # Test moving up in menu
        state_manager.select_previous_option()
        assert state_manager.selected_option == initial_option

    def test_invalid_state_transition(self, state_manager):
        """Test handling of invalid state transitions."""
        # Set initial state to MAIN_MENU
        state_manager.change_state(GameState.MAIN_MENU)
        assert state_manager.current_state == GameState.MAIN_MENU
        
        # Test invalid transition
        with pytest.raises(ValueError):
            state_manager.change_state("INVALID_STATE")
        
        # State should remain unchanged
        assert state_manager.current_state == GameState.MAIN_MENU

class TestUIRendering:
    def test_menu_rendering(self, pygame_init, game):
        """Test menu rendering."""
        screen = pygame.display.set_mode((800, 600))
        # No need to change state since it's already in MAIN_MENU
        game.render()  # Should not raise any errors
        assert screen is not None
        assert screen.get_width() == 800
        assert screen.get_height() == 600

    def test_score_display(self, pygame_init, game):
        """Test score display rendering."""
        game.score = 1000
        font = pygame.font.Font(None, 36)
        text = font.render(f"Score: {game.score}", True, (255, 255, 255))
        assert text is not None
        assert isinstance(text, pygame.Surface)

    def test_game_over_screen(self, pygame_init, game):
        """Test game over screen rendering."""
        # First transition to PLAYING, then to GAME_OVER
        game.state_manager.change_state(GameState.PLAYING)
        game.state_manager.change_state(GameState.GAME_OVER)
        font = pygame.font.Font(None, 48)
        text = font.render("GAME OVER", True, (255, 0, 0))
        assert text is not None
        assert isinstance(text, pygame.Surface)

class TestInputHandling:
    def test_keyboard_input(self, pygame_init, game):
        """Test keyboard input handling."""
        # Simulate key press
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE})
        game.handle_input(event)  # Should not raise any errors
        assert event.type == pygame.KEYDOWN
        assert event.key == pygame.K_SPACE

    def test_pause_input(self, state_manager, pygame_init):
        """Test pause functionality."""
        # First transition to MAIN_MENU, then to PLAYING
        state_manager.change_state(GameState.MAIN_MENU)
        state_manager.change_state(GameState.PLAYING)
        
        # Simulate pause key press
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_p})
        if event.key == pygame.K_p:
            state_manager.change_state(GameState.PAUSED)
        assert state_manager.current_state == GameState.PAUSED
