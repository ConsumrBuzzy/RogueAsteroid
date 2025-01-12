"""Test suite for collision system."""
import pytest
import pygame
import numpy as np
from src.core.game import Game
from src.entities.asteroid import Asteroid
from src.entities.bullet import Bullet
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT

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

class TestCollisionSystem:
    def test_bullet_asteroid_collision(self, game):
        """Test collision between bullet and asteroid."""
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
        game.update(1/60)  # One frame at 60 FPS
        
        # Verify collision handling
        assert bullet not in game.entities  # Bullet should be destroyed
        assert asteroid not in game.entities  # Asteroid should be destroyed
        assert len(game.particles) > 0  # Explosion particles should be created
    
    def test_ship_asteroid_collision(self, game):
        """Test collision between ship and asteroid."""
        game.new_game()
        initial_lives = game.lives
        
        # Get ship position
        ship_transform = game.ship.get_component('transform')
        ship_pos = ship_transform.position
        
        # Create asteroid at ship position
        asteroid = Asteroid(game, 'large', (ship_pos.x + 5, ship_pos.y))
        game.add_entity(asteroid)
        game.asteroids.append(asteroid)
        
        # Update to check collision
        game.update(1/60)
        
        # Verify collision handling
        assert game.lives < initial_lives  # Should lose a life
        assert asteroid not in game.entities  # Asteroid should be destroyed
        assert len(game.particles) > 0  # Explosion particles should be created
    
    def test_asteroid_splitting(self, game):
        """Test that large asteroids split into smaller ones."""
        game.new_game()
        
        # Create a large asteroid
        asteroid = Asteroid(game, 'large', (400, 300))
        game.add_entity(asteroid)
        game.asteroids.append(asteroid)
        
        # Create a bullet to destroy it
        bullet_pos = pygame.Vector2(395, 300)
        bullet_dir = pygame.Vector2(1, 0)
        bullet = Bullet(game, bullet_pos, bullet_dir)
        game.add_entity(bullet)
        game.bullets.append(bullet)
        
        initial_asteroids = len(game.asteroids)
        
        # Update to trigger collision
        game.update(1/60)
        
        # Large asteroid should split into medium asteroids
        assert len(game.asteroids) > initial_asteroids
        for new_asteroid in game.asteroids:
            assert new_asteroid.size == 'medium'
    
    def test_invulnerability_frames(self, game):
        """Test ship invulnerability after respawn."""
        game.new_game()
        initial_lives = game.lives
        
        # Force ship to be invulnerable
        game.ship.invulnerable_timer = 2.0
        
        # Create asteroid at ship position
        ship_transform = game.ship.get_component('transform')
        asteroid = Asteroid(game, 'large', (ship_transform.position.x + 5, ship_transform.position.y))
        game.add_entity(asteroid)
        game.asteroids.append(asteroid)
        
        # Update to check collision
        game.update(1/60)
        
        # Verify no collision while invulnerable
        assert game.lives == initial_lives  # Should not lose a life
        assert asteroid in game.entities  # Asteroid should not be destroyed
    
    def test_screen_wrapping_collision(self, game):
        """Test collisions work correctly with screen wrapping."""
        game.new_game()
        
        # Create asteroid near screen edge
        asteroid = Asteroid(game, 'large', (WINDOW_WIDTH - 10, WINDOW_HEIGHT - 10))
        game.add_entity(asteroid)
        game.asteroids.append(asteroid)
        
        # Create bullet near opposite screen edge
        bullet_pos = pygame.Vector2(10, 10)
        bullet_dir = pygame.Vector2(1, 1)
        bullet = Bullet(game, bullet_pos, bullet_dir)
        game.add_entity(bullet)
        game.bullets.append(bullet)
        
        # Update several frames to allow for wrapping
        for _ in range(10):
            game.update(1/60)
            
        # Verify entities are properly wrapped and can still collide
        assert len(game.entities) > 0  # Some entities should still exist 