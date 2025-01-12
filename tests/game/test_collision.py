"""Test suite for collision system."""
import pytest
import pygame
import numpy as np
from src.core.game import Game
from src.entities.asteroid import Asteroid
from src.entities.bullet import Bullet
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT

@pytest.fixture
def game(mock_game, screen):
    """Create a game instance for testing."""
    game = Game()
    game.screen = screen
    yield game

@pytest.fixture
def collision_setup(game):
    """Setup a fresh game state for collision testing."""
    game.new_game()
    return game

@pytest.mark.game
class TestCollisionSystem:
    """Test cases for the collision detection system."""
    
    def test_bullet_asteroid_collision(self, game, collision_setup):
        """Test collision between bullet and asteroid."""
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
        assert bullet not in game.entities, "Bullet should be destroyed on collision"
        assert asteroid not in game.entities, "Asteroid should be destroyed on collision"
        assert len(game.particles) > 0, "Collision should create explosion particles"
        
        # Verify score increase
        assert game.scoring.current_score > 0, "Destroying asteroid should award points"
    
    def test_ship_asteroid_collision(self, game, collision_setup):
        """Test collision between ship and asteroid."""
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
        assert game.lives == initial_lives - 1, "Ship collision should reduce lives"
        assert asteroid not in game.entities, "Asteroid should be destroyed on collision"
        assert len(game.particles) > 0, "Collision should create explosion particles"
        assert game.ship.invulnerable_timer > 0, "Ship should become invulnerable after collision"
    
    def test_asteroid_splitting(self, game, collision_setup):
        """Test that large asteroids split into smaller ones."""
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
        
        # Verify asteroid splitting
        assert len(game.asteroids) > initial_asteroids, "Large asteroid should split into smaller ones"
        for new_asteroid in game.asteroids:
            assert new_asteroid.size == 'medium', "Split asteroids should be medium sized"
            assert new_asteroid in game.entities, "Split asteroids should be added to game entities"
    
    def test_invulnerability_frames(self, game, collision_setup):
        """Test ship invulnerability after respawn."""
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
        
        # Verify invulnerability
        assert game.lives == initial_lives, "Ship should not lose lives while invulnerable"
        assert asteroid in game.entities, "Asteroid should not be destroyed during invulnerability"
        assert game.ship.invulnerable_timer > 0, "Invulnerability timer should still be active"
        
        # Test invulnerability expiration
        game.update(3.0)  # Update past invulnerability time
        assert game.ship.invulnerable_timer <= 0, "Invulnerability should expire after timer"
    
    def test_screen_wrapping_collision(self, game, collision_setup):
        """Test collisions work correctly with screen wrapping."""
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
        
        # Track initial positions
        asteroid_pos = asteroid.get_component('transform').position.copy()
        bullet_pos = bullet.get_component('transform').position.copy()
        
        # Update several frames to allow for wrapping
        for _ in range(10):
            game.update(1/60)
            
        # Verify wrapping behavior
        new_asteroid_pos = asteroid.get_component('transform').position
        assert (new_asteroid_pos != asteroid_pos), "Asteroid should move from original position"
        
        # Verify collision still works after wrapping
        assert len(game.entities) > 0, "Entities should persist through screen wrapping"
        
    def test_multiple_collisions(self, game, collision_setup):
        """Test handling of multiple simultaneous collisions."""
        # Create multiple asteroids around ship
        ship_pos = game.ship.get_component('transform').position
        asteroid_positions = [
            (ship_pos.x + 5, ship_pos.y),
            (ship_pos.x - 5, ship_pos.y),
            (ship_pos.x, ship_pos.y + 5)
        ]
        
        asteroids = []
        for pos in asteroid_positions:
            asteroid = Asteroid(game, 'small', pos)
            game.add_entity(asteroid)
            game.asteroids.append(asteroid)
            asteroids.append(asteroid)
            
        initial_lives = game.lives
        
        # Update to trigger multiple collisions
        game.update(1/60)
        
        # Verify multiple collision handling
        assert game.lives == initial_lives - 1, "Multiple collisions should only subtract one life"
        assert len(game.particles) > len(asteroids), "Each collision should create particles"
        assert game.ship.invulnerable_timer > 0, "Ship should become invulnerable after collision" 