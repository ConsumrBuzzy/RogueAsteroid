"""Test suite for physics and collision detection."""
import pytest
import pygame
import numpy as np
from src.entities.ship import Ship
from src.entities.asteroid import Asteroid
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from src.core.game import Game

@pytest.fixture
def game():
    """Fixture to create a game instance."""
    return Game()

@pytest.fixture
def ship(game):
    """Fixture to create a ship instance."""
    return Ship(game)

@pytest.fixture
def asteroid(game):
    """Fixture to create an asteroid instance."""
    position = pygame.Vector2(100, 100)
    return Asteroid(game, 'large', position)

class TestPhysics:
    def test_velocity_application(self, ship):
        """Test velocity affects position correctly."""
        transform = ship.get_component('transform')
        initial_pos = pygame.Vector2(transform.position)
        ship.thrust = True
        ship.update(1.0)  # Update with 1 second delta time
        new_pos = pygame.Vector2(transform.position)
        assert new_pos != initial_pos

    def test_acceleration(self, ship):
        """Test acceleration affects velocity correctly."""
        physics = ship.get_component('physics')
        initial_velocity = pygame.Vector2(physics.velocity)
        ship.thrust = True
        ship.update(1.0)
        new_velocity = pygame.Vector2(physics.velocity)
        assert new_velocity != initial_velocity

    def test_drag_effect(self, ship):
        """Test drag reduces velocity over time."""
        physics = ship.get_component('physics')
        physics.velocity = pygame.Vector2(10.0, 10.0)
        initial_speed = physics.velocity.length()
        ship.update(1.0)
        new_speed = physics.velocity.length()
        assert new_speed < initial_speed

class TestCollisionDetection:
    def test_point_circle_collision(self, asteroid):
        """Test point-circle collision detection."""
        # Point inside asteroid
        point = (asteroid.x, asteroid.y)
        assert asteroid.point_in_hitbox(point[0], point[1])
        
        # Point outside asteroid
        point = (asteroid.x + asteroid.radius * 2, asteroid.y + asteroid.radius * 2)
        assert not asteroid.point_in_hitbox(point[0], point[1])

    def test_circle_circle_collision(self, ship, asteroid):
        """Test circle-circle collision detection."""
        # Place objects at same position
        ship.x = asteroid.x
        ship.y = asteroid.y
        assert ship.collides_with(asteroid)
        
        # Move ship away by more than combined radii
        ship.x = asteroid.x + (ship.radius + asteroid.radius) * 2
        assert not ship.collides_with(asteroid)

    def test_edge_case_collisions(self, ship, asteroid):
        """Test edge cases in collision detection."""
        # Test exact edge collision
        ship.x = asteroid.x + ship.radius + asteroid.radius
        ship.y = asteroid.y
        # Should not collide when exactly at edge
        assert not ship.collides_with(asteroid)
        
        # Move slightly closer
        ship.x -= 1
        # Should collide when slightly overlapping
        assert ship.collides_with(asteroid)

class TestBoundaryWrapping:
    def test_horizontal_wrapping(self, ship):
        """Test horizontal screen wrapping."""
        ship.x = WINDOW_WIDTH + 10
        ship.update(0.016)
        assert ship.x < ship.radius

        ship.x = -10
        ship.update(0.016)
        assert ship.x > WINDOW_WIDTH - ship.radius

    def test_vertical_wrapping(self, ship):
        """Test vertical screen wrapping."""
        ship.y = WINDOW_HEIGHT + 10
        ship.update(0.016)
        assert ship.y < ship.radius

        ship.y = -10
        ship.update(0.016)
        assert ship.y > WINDOW_HEIGHT - ship.radius

    def test_diagonal_wrapping(self, ship):
        """Test diagonal screen wrapping."""
        ship.x = WINDOW_WIDTH + 10
        ship.y = WINDOW_HEIGHT + 10
        ship.update(0.016)
        assert ship.x < ship.radius
        assert ship.y < ship.radius
