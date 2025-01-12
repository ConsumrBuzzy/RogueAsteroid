"""Test suite for core game systems."""
import pytest
import pygame
import numpy as np
from src.core.game_state import GameState, StateManager
from src.core.scoring import ScoringSystem
from src.core.game import Game
from src.core.constants import *

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

class TestScoreSystem:
    def test_score_tracking(self, game):
        """Test basic score functionality"""
        initial_score = game.scoring.current_score
        game.scoring.add_points(100)
        assert game.scoring.current_score > initial_score
    
    def test_high_score_tracking(self, game):
        """Test high score tracking"""
        game.new_game()  # Start a new game first
        game.scoring.reset()  # Reset scoring to ensure clean state
        game.scoring.add_points(10000)  # Add enough points to beat default high score
        assert game.scoring.check_high_score()  # Should be a high score since we reset
        
        # Add a high score and verify it was added
        game.scoring.add_high_score("TEST", 1)
        high_scores = game.scoring.get_high_scores()
        assert len(high_scores) > 0
        assert high_scores[0].score == 10000
        
    def test_score_reset(self, game):
        """Test score reset functionality"""
        game.scoring.add_points(500)
        game.scoring.reset()
        assert game.scoring.current_score == 0
        
    def test_high_score_persistence(self, game):
        """Test high score saving and loading"""
        game.scoring.add_points(10000)
        name = "TEST"
        level = 1
        game.scoring.add_high_score(name, level)
        high_scores = game.scoring.get_high_scores()
        assert len(high_scores) > 0
        assert high_scores[0].score >= 10000
        assert high_scores[0].name == name

class TestGame:
    def test_game_initialization(self, game):
        """Test game initialization"""
        assert game.screen is not None
        assert game.width == WINDOW_WIDTH
        assert game.height == WINDOW_HEIGHT
    
    def test_game_reset(self, game):
        """Test game reset functionality"""
        game.new_game()  # First start a game
        game.scoring.add_points(1000)  # Add some score
        game.reset_game()  # Then reset
        assert game.scoring.current_score == 0
        assert game.level == 1
        assert game.lives == STARTING_LIVES
        
    def test_asteroid_spawning(self, game):
        """Test asteroid spawning"""
        game.new_game()
        initial_asteroids = len(game.asteroids)
        game.spawn_asteroid_wave()
        assert len(game.asteroids) > initial_asteroids

class TestParticleEffects:
    def test_thrust_particles(self, game):
        """Test thrust particle creation"""
        game.new_game()
        assert game.ship is not None, "Ship should exist after new_game()"
        
        initial_particles = len(game.particles)
        
        # Get input component and simulate thrust
        input_component = game.ship.get_component('input')
        assert input_component is not None, "Ship should have input component"
        
        # Simulate thrusting for multiple frames to ensure particles are created
        for _ in range(5):  # Simulate for 5 frames
            input_component.handle_keydown(pygame.K_UP)  # Simulate pressing UP key
            game.update(0.016)  # Update one frame
        
        input_component.handle_keyup(pygame.K_UP)  # Release key
        game.update(0.016)  # One more update
        
        assert len(game.particles) > initial_particles, "Thrusting should create particles"
    
    def test_explosion_particles(self, game):
        """Test explosion particle creation"""
        game.new_game()
        initial_particles = len(game.particles)
        game.create_explosion(400, 300)
        assert len(game.particles) > initial_particles
        
    def test_particle_cleanup(self, game):
        """Test particle cleanup"""
        game.new_game()
        game.create_explosion(400, 300)
        initial_particles = len(game.particles)
        
        # Update for long enough to expire particles
        # Most particles have lifetime between 0.5 and 1.0 seconds
        # Update for 1.5 seconds to ensure all particles expire
        total_time = 1.5  # seconds
        frame_time = 0.016  # 60 FPS
        frames = int(total_time / frame_time)
        
        for _ in range(frames):
            game.update(frame_time)
        
        assert len(game.particles) < initial_particles

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