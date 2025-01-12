import pytest
import pygame
from src.core.game_state import GameState, StateManager
from src.core.scoring import ScoringSystem
from src.core.spawner import Spawner
from src.core.particles import ParticleSystem
from src.core.menu import MainMenu, OptionsMenu
from src.core.game import Game
from src.core.constants import *

class TestGameState:
    @pytest.fixture
    def state_manager(self):
        return StateManager()
    
    def test_state_transitions(self, state_manager):
        """Test game state transitions"""
        assert state_manager.current_state == GameState.MENU
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
    def score_system(self):
        return ScoringSystem()
    
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
        game.reset_game()
        assert game.score == 0
        assert len(game.asteroids) == 0
        
    def test_asteroid_spawning(self, game):
        """Test asteroid spawning"""
        game.spawn_asteroid_wave()
        assert len(game.asteroids) > 0

class TestParticleSystem:
    @pytest.fixture
    def game(self):
        pygame.init()
        return Game()
    
    @pytest.fixture
    def particle_system(self, game):
        return ParticleSystem(game)
    
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
        return Game()
    
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
        initial_scheme = options_menu.game.settings.get('control_scheme', 'arrows')
        options_menu.toggle_control_scheme()
        current_scheme = options_menu.game.settings.get('control_scheme', 'arrows')
        assert current_scheme != initial_scheme
    
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