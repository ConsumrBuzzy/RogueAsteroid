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
        """Test that adding points correctly updates high score."""
        # Start new game and reset scoring
        game.new_game()
        game.scoring.reset()
        
        # Clear existing high scores
        game.scoring.high_scores = []
        
        # Add points and verify score
        game.scoring.add_points(10000)
        assert game.scoring.current_score == 10000
        
        # Should be a high score since we cleared the list
        assert game.scoring.check_high_score()
        
        # Add high score and verify
        assert game.scoring.add_high_score("TEST", 1)
        assert len(game.scoring.high_scores) == 1
        assert game.scoring.high_scores[0].score == 10000
        assert game.scoring.high_scores[0].name == "TEST"
        
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
    def test_thrust_particle_creation(self, game):
        """Test that thrust particles are created."""
        game.new_game()
        assert game.ship is not None
        initial_particles = len(game.particles)
        game.ship.create_thrust_particles()
        assert len(game.particles) > initial_particles

    def test_thrust_particle_input(self, game):
        """Test that thrust particles are created when UP key is pressed."""
        game.new_game()
        input_comp = game.ship.get_component('input')
        assert input_comp is not None
        
        # Simulate thrust key press
        input_comp.handle_keydown(pygame.K_UP)
        assert pygame.K_UP in input_comp.active_keys
        
        # Update a few frames
        initial_particles = len(game.particles)
        for _ in range(5):
            game.update(1/60)
        assert len(game.particles) > initial_particles

    def test_thrust_particle_cleanup(self, game):
        """Test that thrust particles are removed after lifetime expires."""
        game.new_game()
        game.ship.create_thrust_particles()
        initial_particles = len(game.particles)
        assert initial_particles > 0
        
        # Update long enough for particles to expire
        total_time = 0.5  # Most thrust particles live 0.1-0.3 seconds
        for _ in range(int(total_time * 60)):  # 60 FPS
            game.update(1/60)
        assert len(game.particles) < initial_particles
        
    def test_explosion_particle_creation(self, game):
        """Test that explosion creates correct number of particles."""
        game.new_game()
        initial_particles = len(game.particles)
        game.create_explosion(400, 300)
        new_particles = len(game.particles) - initial_particles
        assert 8 <= new_particles <= 12  # From create_explosion method
        
    def test_explosion_particle_cleanup(self, game):
        """Test that explosion particles are removed after lifetime expires."""
        game.new_game()
        game.create_explosion(400, 300)
        initial_particles = len(game.particles)
        assert initial_particles > 0
        
        # Update long enough for particles to expire
        total_time = 1.5  # Most explosion particles live 0.5-1.0 seconds
        for _ in range(int(total_time * 60)):  # 60 FPS
            game.update(1/60)
        assert len(game.particles) == 0

    def test_particle_velocity(self, game):
        """Test that particles move according to their velocity."""
        game.new_game()
        test_pos = pygame.Vector2(400, 300)
        game.create_explosion(test_pos.x, test_pos.y)
        
        # Get initial positions
        initial_positions = [pygame.Vector2(p['position']) for p in game.particles]
        
        # Update one frame
        game.update(1/60)
        
        # Verify particles have moved
        for i, particle in enumerate(game.particles):
            current_pos = pygame.Vector2(particle['position'])
            assert current_pos != initial_positions[i]

    def test_particle_color(self, game):
        """Test that particles maintain their color."""
        game.new_game()
        game.create_explosion(400, 300)
        for particle in game.particles:
            assert 'color' in particle
            assert len(particle['color']) == 3  # RGB tuple
            assert all(0 <= c <= 255 for c in particle['color'])

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