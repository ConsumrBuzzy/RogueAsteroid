import pytest
import pygame
from src.core.game_state import GameState
from src.core.scoring import ScoringSystem
from src.core.spawner import Spawner
from src.core.particles import ParticleSystem
from src.core.menu import MainMenu, OptionsMenu
from src.core.game import Game
from src.core.constants import *

class TestGameState:
    @pytest.fixture
    def game_state(self):
        return GameState()
    
    def test_state_transitions(self, game_state):
        """Test game state transitions"""
        assert game_state.current_state == MENU_STATE
        game_state.start_game()
        assert game_state.current_state == PLAYING_STATE
        game_state.pause_game()
        assert game_state.current_state == PAUSED_STATE
        game_state.resume_game()
        assert game_state.current_state == PLAYING_STATE
        game_state.game_over()
        assert game_state.current_state == GAME_OVER_STATE
    
    def test_level_management(self, game_state):
        """Test level progression"""
        game_state.start_game()
        initial_level = game_state.current_level
        game_state.advance_level()
        assert game_state.current_level == initial_level + 1
        
    def test_lives_system(self, game_state):
        """Test lives management"""
        game_state.start_game()
        initial_lives = game_state.lives
        game_state.lose_life()
        assert game_state.lives == initial_lives - 1
        game_state.add_life()
        assert game_state.lives == initial_lives

class TestScoreSystem:
    @pytest.fixture
    def score_system(self):
        return ScoringSystem()
    
    def test_score_tracking(self, score_system):
        """Test basic score functionality"""
        initial_score = score_system.current_score
        score_system.add_points(100)
        assert score_system.current_score == initial_score + 100
    
    def test_high_score_tracking(self, score_system):
        """Test high score tracking"""
        score_system.add_points(1000)
        assert score_system.check_high_score()
        
    def test_score_reset(self, score_system):
        """Test score reset functionality"""
        score_system.add_points(500)
        score_system.reset()
        assert score_system.current_score == 0
        
    def test_high_score_persistence(self, score_system):
        """Test high score saving and loading"""
        score_system.add_points(2000)
        name = "TEST"
        level = 1
        score_system.add_high_score(name, level)
        high_scores = score_system.get_high_scores()
        assert len(high_scores) > 0
        assert high_scores[0].score == 2000
        assert high_scores[0].name == name

class TestSpawner:
    @pytest.fixture
    def game(self):
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        return Game(screen)
    
    @pytest.fixture
    def spawner(self, game):
        return Spawner(game)
    
    def test_wave_progression(self, spawner):
        """Test wave progression"""
        initial_wave = spawner.wave
        spawner.advance_wave()
        assert spawner.wave == initial_wave + 1
    
    def test_asteroid_spawning(self, spawner):
        """Test asteroid spawning"""
        spawner.start_wave()
        assert len(spawner.game.asteroids) > 0
    
    def test_wave_completion(self, spawner):
        """Test wave completion detection"""
        spawner.start_wave()
        spawner.game.asteroids.clear()  # Remove all asteroids
        assert spawner.check_wave_complete()

class TestParticleSystem:
    @pytest.fixture
    def particle_system(self):
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        return ParticleSystem(screen)
    
    def test_particle_creation(self, particle_system):
        """Test particle creation and lifecycle"""
        initial_count = len(particle_system.particles)
        particle_system.create_explosion(400, 300)
        assert len(particle_system.particles) > initial_count
    
    def test_particle_update(self, particle_system):
        """Test particle updating"""
        particle_system.create_thrust(400, 300, 0)
        initial_particles = len(particle_system.particles)
        particle_system.update(1.0)  # Update with 1 second delta
        assert len(particle_system.particles) <= initial_particles  # Particles should decay
        
    def test_particle_cleanup(self, particle_system):
        """Test particle cleanup"""
        particle_system.create_thrust(400, 300, 0)
        particle_system.update(10.0)  # Long update to expire particles
        assert len(particle_system.particles) == 0

class TestMenu:
    @pytest.fixture
    def game(self):
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        return Game(screen)
    
    @pytest.fixture
    def main_menu(self, game):
        return MainMenu(game)
    
    @pytest.fixture
    def options_menu(self, game):
        return OptionsMenu(game)
    
    def test_main_menu_options(self, main_menu):
        """Test main menu has correct options"""
        assert len(main_menu.items) > 0
        assert any(item.text == "Start Game" for item in main_menu.items)
        assert any(item.text == "Options" for item in main_menu.items)
        assert any(item.text == "Quit" for item in main_menu.items)
    
    def test_options_menu(self, options_menu):
        """Test options menu functionality"""
        initial_scheme = options_menu.game.control_scheme
        options_menu.toggle_control_scheme()
        assert options_menu.game.control_scheme != initial_scheme
    
    def test_menu_navigation(self, main_menu):
        """Test menu navigation"""
        initial_selected = None
        for item in main_menu.items:
            if item.selected:
                initial_selected = item
                break
        
        # Simulate down key press
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_DOWN})
        main_menu.handle_input(event)
        
        current_selected = None
        for item in main_menu.items:
            if item.selected:
                current_selected = item
                break
        
        assert current_selected != initial_selected 