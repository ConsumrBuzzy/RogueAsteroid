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

class TestGameplayFlow:
    def test_game_initialization_flow(self, game):
        """Test complete game initialization sequence."""
        # Check initial state
        assert game.state_manager.current_state == GameState.MAIN_MENU
        assert game.scoring.current_score == 0
        assert len(game.asteroids) == 0
        assert game.ship is None
        
        # Start new game
        game.new_game()
        assert game.state_manager.current_state == GameState.PLAYING
        assert game.ship is not None
        assert isinstance(game.ship, Ship)
        assert len(game.asteroids) > 0  # Initial wave spawned
        
        # Verify ship components
        transform = game.ship.get_component('transform')
        assert transform is not None, "Ship should have transform component"
        assert hasattr(transform, 'position')
        assert hasattr(transform, 'velocity')
        assert transform.position.x == WINDOW_WIDTH // 2  # Ship should start in center
        assert transform.position.y == WINDOW_HEIGHT // 2
        
        # Verify other required components
        assert game.ship.get_component('input') is not None
        assert game.ship.get_component('collision') is not None
    
    def test_wave_progression(self, game):
        """Test wave system and asteroid spawning."""
        game.new_game()
        initial_wave = game.level
        initial_asteroids = len(game.asteroids)
        
        # Clear asteroids to trigger next wave
        game.asteroids.clear()
        game.update(1.0)  # Update to check wave completion
        
        assert game.level > initial_wave
        assert len(game.asteroids) >= initial_asteroids
    
    def test_scoring_integration(self, game):
        """Test scoring system integration with gameplay."""
        game.new_game()
        initial_score = game.scoring.current_score
        
        # Create a test bullet and asteroid
        bullet_pos = pygame.Vector2(400, 300)
        bullet_dir = pygame.Vector2(1, 0)  # Shooting right
        bullet = Bullet(game, bullet_pos, bullet_dir)
        game.add_entity(bullet)
        game.bullets.append(bullet)
        
        # Create a test asteroid near the bullet
        asteroid = Asteroid(game, 'large', (bullet_pos.x + 5, bullet_pos.y))
        game.add_entity(asteroid)
        game.asteroids.append(asteroid)
        
        # Update to trigger collision
        game.update(0.016)
        
        # Score should have increased from destroying asteroid
        assert game.scoring.current_score > initial_score, "Score should increase when asteroid is destroyed"
        
        # Verify asteroid was removed
        assert asteroid not in game.asteroids, "Asteroid should be removed after collision"
        assert bullet not in game.bullets, "Bullet should be removed after collision"
    
    def test_collision_system(self, game):
        """Test collision detection and response."""
        game.new_game()
        
        # Create a test bullet
        bullet_pos = pygame.Vector2(400, 300)
        bullet_dir = pygame.Vector2(1, 0)  # Shooting right
        bullet = Bullet(game, bullet_pos, bullet_dir)
        game.add_entity(bullet)
        game.bullets.append(bullet)
        
        # Create a test asteroid near the bullet
        asteroid = Asteroid(game, 'large', (bullet_pos.x + 5, bullet_pos.y))
        game.add_entity(asteroid)
        game.asteroids.append(asteroid)
        
        # Update to check collisions
        game.update(0.016)  # One frame at 60 FPS
        
        # Verify collision handling
        assert bullet not in game.entities  # Bullet should be destroyed
        assert asteroid not in game.entities  # Asteroid should be destroyed
    
    def test_game_over_sequence(self, game):
        """Test game over sequence and state transitions."""
        game.new_game()
        initial_lives = game.lives
        
        # Reset scoring and add points
        game.scoring.reset()  # Clear any existing scores
        game.scoring.add_points(10000)  # Add enough points to beat default high score
        
        # Simulate losing all lives
        for _ in range(initial_lives):
            game.lose_life()
            game.update(0.016)  # Update to process life loss
        
        assert game.state_manager.current_state == GameState.GAME_OVER
        
        # Should be a high score since we reset and added points
        assert game.scoring.check_high_score(), "Should be a high score after adding 10000 points"
        
        # Add the high score and verify
        game.scoring.add_high_score("TEST", game.level)
        high_scores = game.scoring.get_high_scores()
        assert len(high_scores) > 0, "High scores list should not be empty"
        assert high_scores[0].score == 10000, "First high score should be 10000"
        assert high_scores[0].name == "TEST", "First high score should be from TEST player"
    
    def test_pause_resume_flow(self, game):
        """Test pause and resume functionality."""
        game.new_game()
        
        # Record initial state
        initial_asteroids = [(a, a.get_component('transform').position.copy()) for a in game.asteroids]
        initial_ship_pos = game.ship.get_component('transform').position.copy()
        
        # Pause game
        game.pause()
        assert game.state_manager.current_state == GameState.PAUSED
        
        # Update while paused
        game.update(1.0)
        
        # Verify nothing moved while paused
        for asteroid, initial_pos in initial_asteroids:
            current_pos = asteroid.get_component('transform').position
            assert abs(current_pos.x - initial_pos.x) < 0.001, "X position changed while paused"
            assert abs(current_pos.y - initial_pos.y) < 0.001, "Y position changed while paused"
        
        current_ship_pos = game.ship.get_component('transform').position
        assert abs(current_ship_pos.x - initial_ship_pos.x) < 0.001, "Ship X position changed while paused"
        assert abs(current_ship_pos.y - initial_ship_pos.y) < 0.001, "Ship Y position changed while paused"
        
        # Resume game
        game.resume()
        assert game.state_manager.current_state == GameState.PLAYING
        
        # Update and verify movement resumes
        game.update(1.0)
        any_moved = False
        for asteroid, initial_pos in initial_asteroids:
            current_pos = asteroid.get_component('transform').position
            if (abs(current_pos.x - initial_pos.x) > 0.001 or 
                abs(current_pos.y - initial_pos.y) > 0.001):
                any_moved = True
                break
        assert any_moved, "No asteroids moved after resuming"
    
    def test_particle_effects_integration(self, game):
        """Test particle system integration."""
        game.new_game()
        initial_particles = len(game.particles)
        
        # Trigger ship thrust using input component
        input_component = game.ship.get_component('input')
        assert input_component is not None
        
        # Simulate thrusting for a few frames
        for _ in range(5):
            input_component.handle_keydown(pygame.K_UP)
            game.update(0.016)
        
        assert len(game.particles) > initial_particles, "Thrusting should create particles"
        
        # Simulate asteroid destruction
        if len(game.asteroids) > 0:
            asteroid = game.asteroids[0]
            pos = asteroid.get_component('transform').position
            game.create_explosion(pos.x, pos.y)  # Create explosion at asteroid position
            game.remove_entity(asteroid)  # Remove the asteroid
            game.asteroids.remove(asteroid)
            assert len(game.particles) > initial_particles, "Explosion should create particles"
    
    def test_complete_game_cycle(self, game):
        """Test a complete game cycle from start to finish."""
        # Start game
        game.new_game()
        assert game.state_manager.current_state == GameState.PLAYING
        
        # Play through one wave
        initial_wave = game.level
        game.asteroids.clear()  # Clear wave
        game.update(1.0)
        assert game.level > initial_wave
        
        # Trigger game over
        while game.lives > 0:
            game.lose_life()
        game.update(0.016)
        
        assert game.state_manager.current_state == GameState.GAME_OVER
        
        # Return to menu
        game.return_to_menu()
        assert game.state_manager.current_state == GameState.MAIN_MENU 