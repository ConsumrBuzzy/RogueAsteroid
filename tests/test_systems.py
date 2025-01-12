import pytest
import pygame
from src.core.game_state import GameState
from src.core.scoring import ScoreManager
from src.core.spawner import SpawnSystem
from src.core.particles import ParticleSystem
from src.core.audio import AudioSystem
from src.core.menu import MenuSystem
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

class TestScoreManager:
    @pytest.fixture
    def score_manager(self):
        return ScoreManager()
    
    def test_score_tracking(self, score_manager):
        """Test basic score functionality"""
        initial_score = score_manager.current_score
        score_manager.add_points(100)
        assert score_manager.current_score == initial_score + 100
    
    def test_high_score_tracking(self, score_manager):
        """Test high score tracking"""
        score_manager.add_points(1000)
        assert score_manager.is_high_score(score_manager.current_score)

class TestSpawnSystem:
    @pytest.fixture
    def spawn_system(self):
        return SpawnSystem()
    
    def test_asteroid_spawning(self, spawn_system):
        """Test asteroid spawning logic"""
        asteroids = spawn_system.spawn_asteroids(level=1)
        assert len(asteroids) > 0
        assert all(asteroid.size in ['large', 'medium', 'small'] for asteroid in asteroids)

class TestParticleSystem:
    @pytest.fixture
    def particle_system(self):
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
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

class TestAudioSystem:
    @pytest.fixture
    def audio_system(self):
        return AudioSystem()
    
    def test_sound_playing(self, audio_system):
        """Test sound effect playing"""
        audio_system.play_sound('shoot')
        assert audio_system.is_sound_playing('shoot')

class TestMenuSystem:
    @pytest.fixture
    def menu_system(self):
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        return MenuSystem(screen)
    
    def test_menu_navigation(self, menu_system):
        """Test menu navigation"""
        initial_option = menu_system.selected_option
        menu_system.move_cursor_down()
        assert menu_system.selected_option != initial_option
        menu_system.move_cursor_up()
        assert menu_system.selected_option == initial_option 