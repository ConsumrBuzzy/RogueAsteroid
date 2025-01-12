import pytest
import pygame
from src.core.game_state import GameState
from src.core.scoring import ScoringSystem
from src.core.spawner import SpawnSystem
from src.core.particles import ParticleSystem
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

class TestSpawnSystem:
    @pytest.fixture
    def spawn_system(self):
        return SpawnSystem()
    
    def test_asteroid_spawning(self, spawn_system):
        """Test asteroid spawning logic"""
        asteroids = spawn_system.spawn_asteroids(level=1)
        assert len(asteroids) > 0
        assert all(asteroid.size in ['large', 'medium', 'small'] for asteroid in asteroids)
        
    def test_level_scaling(self, spawn_system):
        """Test asteroid count scaling with level"""
        level1_asteroids = len(spawn_system.spawn_asteroids(level=1))
        level2_asteroids = len(spawn_system.spawn_asteroids(level=2))
        assert level2_asteroids > level1_asteroids
        
    def test_asteroid_properties(self, spawn_system):
        """Test asteroid property initialization"""
        asteroids = spawn_system.spawn_asteroids(level=1)
        for asteroid in asteroids:
            assert hasattr(asteroid, 'velocity')
            assert hasattr(asteroid, 'position')
            assert hasattr(asteroid, 'rotation')

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
        
    def test_particle_properties(self, particle_system):
        """Test particle property initialization"""
        particle_system.create_explosion(400, 300)
        for particle in particle_system.particles:
            assert hasattr(particle, 'position')
            assert hasattr(particle, 'velocity')
            assert hasattr(particle, 'lifetime')
            assert particle.lifetime > 0
            
    def test_particle_cleanup(self, particle_system):
        """Test particle cleanup"""
        particle_system.create_thrust(400, 300, 0)
        particle_system.update(10.0)  # Long update to expire particles
        assert len(particle_system.particles) == 0

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
        
    def test_menu_selection(self, menu_system):
        """Test menu option selection"""
        menu_system.select_option()
        assert menu_system.is_option_selected
        
    def test_menu_bounds(self, menu_system):
        """Test menu navigation bounds"""
        # Move to bottom
        for _ in range(len(menu_system.options)):
            menu_system.move_cursor_down()
        last_option = menu_system.selected_option
        menu_system.move_cursor_down()  # Try to move past bottom
        assert menu_system.selected_option == last_option 