"""Test suite for core game systems."""
import pytest
import pygame
import numpy as np
from src.core.game_state import GameState, StateManager
from src.core.scoring import ScoringSystem
from src.core.game import Game
from src.core.constants import *

class TestGameState:
    @pytest.fixture
    def game(self):
        return Game()
    
    @pytest.fixture
    def state_manager(self, game):
        return game.state_manager
    
    def test_state_transitions(self, state_manager):
        """Test game state transitions"""
        assert state_manager.current_state == GameState.MAIN_MENU
        state_manager.change_state(GameState.PLAYING)
        assert state_manager.current_state == GameState.PLAYING
        state_manager.change_state(GameState.PAUSED)
        assert state_manager.current_state == GameState.PAUSED
        state_manager.change_state(GameState.PLAYING)
        assert state_manager.current_state == GameState.PLAYING
        state_manager.change_state(GameState.GAME_OVER)
        assert state_manager.current_state == GameState.GAME_OVER

class TestScoreSystem:
    @pytest.fixture
    def game(self):
        return Game()
    
    @pytest.fixture
    def score_system(self, game):
        return game.scoring
    
    def test_score_tracking(self, score_system):
        """Test basic score functionality"""
        initial_score = score_system.current_score
        score_system.add_points(100)
        assert score_system.current_score > initial_score
    
    def test_high_score_tracking(self, score_system):
        """Test high score tracking"""
        score_system.add_points(10000)  # Add enough points to beat default high score
        assert score_system.check_high_score()
        
    def test_score_reset(self, score_system):
        """Test score reset functionality"""
        score_system.add_points(500)
        score_system.reset()
        assert score_system.current_score == 0
        
    def test_high_score_persistence(self, score_system):
        """Test high score saving and loading"""
        score_system.add_points(10000)
        name = "TEST"
        level = 1
        score_system.add_high_score(name, level)
        high_scores = score_system.get_high_scores()
        assert len(high_scores) > 0
        assert high_scores[0].score >= 10000
        assert high_scores[0].name == name

class TestGame:
    @pytest.fixture
    def game(self):
        pygame.init()
        return Game()
    
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
    @pytest.fixture
    def game(self):
        pygame.init()
        return Game()
    
    def test_thrust_particles(self, game):
        """Test thrust particle creation"""
        game.new_game()
        initial_particles = len(game.particles)
        game.ship.thrust(1.0)
        assert len(game.particles) > initial_particles
    
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
        for _ in range(60):  # 1 second at 60 FPS
            game.update(0.016)
        assert len(game.particles) < initial_particles

class TestMenu:
    @pytest.fixture
    def game(self):
        pygame.init()
        return Game()
    
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