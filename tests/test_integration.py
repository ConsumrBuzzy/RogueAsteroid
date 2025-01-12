"""Integration tests for RogueAsteroid core systems."""
import pytest
import pygame
import numpy as np
from src.core.game import Game
from src.core.game_state import GameState
from src.entities.asteroid import Asteroid
from src.entities.ship import Ship
from src.entities.bullet import Bullet
from src.core.constants import *

class TestGameplayFlow:
    @pytest.fixture
    def game(self):
        """Initialize game instance for testing."""
        pygame.init()
        return Game()
    
    def test_game_initialization_flow(self, game):
        """Test complete game initialization sequence."""
        # Check initial state
        assert game.state_manager.current_state == GameState.MAIN_MENU
        assert game.score_system.current_score == 0
        assert len(game.asteroids) == 0
        assert game.ship is None
        
        # Start game
        game.start_game()
        assert game.state_manager.current_state == GameState.PLAYING
        assert game.ship is not None
        assert isinstance(game.ship, Ship)
        assert len(game.asteroids) > 0  # Initial wave spawned
        
        # Verify ship properties
        assert hasattr(game.ship, 'position')
        assert hasattr(game.ship, 'velocity')
        assert game.ship.lives == STARTING_LIVES
    
    def test_wave_progression(self, game):
        """Test wave system and asteroid spawning."""
        game.start_game()
        initial_wave = game.spawner.wave
        initial_asteroids = len(game.asteroids)
        
        # Clear asteroids to trigger next wave
        game.asteroids.clear()
        game.update(1.0)  # Update to check wave completion
        
        assert game.spawner.wave > initial_wave
        assert len(game.asteroids) >= initial_asteroids
    
    def test_scoring_integration(self, game):
        """Test scoring system integration with gameplay."""
        game.start_game()
        initial_score = game.score_system.current_score
        
        # Simulate destroying an asteroid
        if len(game.asteroids) > 0:
            asteroid = game.asteroids[0]
            game.handle_asteroid_destroyed(asteroid)
            
            assert game.score_system.current_score > initial_score
    
    def test_collision_system(self, game):
        """Test collision detection and response."""
        game.start_game()
        
        # Create a test bullet
        bullet_pos = np.array([400, 300])
        bullet = Bullet(bullet_pos[0], bullet_pos[1], 0)
        game.add_entity(bullet)
        
        # Create a test asteroid near the bullet
        asteroid = Asteroid(bullet_pos[0] + 5, bullet_pos[1])
        game.add_entity(asteroid)
        
        # Update to check collisions
        game.update(0.016)  # One frame at 60 FPS
        
        # Verify collision handling
        assert bullet not in game.entities  # Bullet should be destroyed
        assert asteroid not in game.entities  # Asteroid should be destroyed
    
    def test_game_over_sequence(self, game):
        """Test game over sequence and state transitions."""
        game.start_game()
        initial_lives = game.ship.lives
        
        # Simulate losing all lives
        for _ in range(initial_lives):
            game.ship.lose_life()
            game.update(0.016)  # Update to process life loss
        
        assert game.state_manager.current_state == GameState.GAME_OVER
        assert game.score_system.check_high_score()  # Should check for high score
    
    def test_pause_resume_flow(self, game):
        """Test pause and resume functionality."""
        game.start_game()
        
        # Record initial state
        initial_asteroids = [a.position.copy() for a in game.asteroids]
        initial_ship_pos = game.ship.position.copy()
        
        # Pause game
        game.pause_game()
        assert game.state_manager.current_state == GameState.PAUSED
        
        # Update while paused
        game.update(1.0)
        
        # Verify nothing moved while paused
        for asteroid, initial_pos in zip(game.asteroids, initial_asteroids):
            assert np.array_equal(asteroid.position, initial_pos)
        assert np.array_equal(game.ship.position, initial_ship_pos)
        
        # Resume game
        game.resume_game()
        assert game.state_manager.current_state == GameState.PLAYING
        
        # Update and verify movement resumes
        game.update(1.0)
        assert any(not np.array_equal(a.position, i) 
                  for a, i in zip(game.asteroids, initial_asteroids))
    
    def test_particle_effects_integration(self, game):
        """Test particle system integration."""
        game.start_game()
        initial_particles = len(game.particle_system.particles)
        
        # Trigger ship thrust
        game.ship.thrust(1.0)
        assert len(game.particle_system.particles) > initial_particles
        
        # Simulate asteroid destruction
        if len(game.asteroids) > 0:
            asteroid = game.asteroids[0]
            game.handle_asteroid_destroyed(asteroid)
            assert len(game.particle_system.particles) > initial_particles
    
    def test_complete_game_cycle(self, game):
        """Test a complete game cycle from start to finish."""
        # Start game
        game.start_game()
        assert game.state_manager.current_state == GameState.PLAYING
        
        # Play through one wave
        initial_wave = game.spawner.wave
        game.asteroids.clear()  # Clear wave
        game.update(1.0)
        assert game.spawner.wave > initial_wave
        
        # Trigger game over
        while game.ship.lives > 0:
            game.ship.lose_life()
        game.update(0.016)
        
        assert game.state_manager.current_state == GameState.GAME_OVER
        
        # Return to menu
        game.return_to_menu()
        assert game.state_manager.current_state == GameState.MAIN_MENU 