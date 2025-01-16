"""Test suite for physics and collision detection."""
import pytest
import pygame
import numpy as np
from src.entities.ship import Ship
from src.entities.asteroid import Asteroid
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from src.core.game import Game
from src.core.entities.base import CollisionComponent, TransformComponent

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
        physics = ship.get_component('physics')
        initial_pos = pygame.Vector2(transform.position)
        physics.apply_force(pygame.Vector2(100000.0, 100000.0))  # Very large force for noticeable movement
        ship.update(0.016)  # Update with 16ms delta time
        new_pos = pygame.Vector2(transform.position)
        assert new_pos != initial_pos

    def test_acceleration(self, ship):
        """Test acceleration affects velocity correctly."""
        physics = ship.get_component('physics')
        transform = ship.get_component('transform')
        initial_velocity = pygame.Vector2(transform.velocity)
        physics.apply_force(pygame.Vector2(1000.0, 1000.0))  # Large enough force for noticeable acceleration
        ship.update(0.016)  # Update with 16ms delta time
        new_velocity = pygame.Vector2(transform.velocity)
        assert new_velocity != initial_velocity

    def test_drag_effect(self, ship):
        """Test drag reduces velocity over time."""
        physics = ship.get_component('physics')
        physics.velocity = pygame.Vector2(100.0, 100.0)  # Set initial velocity
        initial_speed = physics.velocity.length()
        ship.update(0.016)  # Update with 16ms delta time
        new_speed = physics.velocity.length()
        assert new_speed < initial_speed

class TestCollisionDetection:
    def test_circle_circle_collision(self, ship, asteroid):
        """Test collision detection between two circular objects."""
        ship_transform = ship.get_component('transform')
        ship_collision = ship.get_component('collision')
        asteroid_transform = asteroid.get_component('transform')
        asteroid_collision = asteroid.get_component('collision')
        
        # Position objects to collide
        ship_transform.position = pygame.Vector2(100, 100)
        asteroid_transform.position = pygame.Vector2(110, 110)
        
        # Check collision
        assert ship_collision.check_collision(asteroid_collision)

    def test_point_circle_collision(self, ship):
        """Test collision detection between a point and a circular object."""
        transform = ship.get_component('transform')
        collision = ship.get_component('collision')
        
        # Create a point collision component with a mock entity
        class MockEntity:
            def __init__(self):
                self.transform = TransformComponent(self)
                self.transform.position = pygame.Vector2(transform.position.x + collision.radius/2, 
                                                      transform.position.y)
                
            def get_component(self, name):
                if name == 'transform':
                    return self.transform
                return None
        
        point_entity = MockEntity()
        point_collision = CollisionComponent(point_entity, radius=0)
        assert collision.check_collision(point_collision)

    def test_edge_case_collisions(self, ship, asteroid):
        """Test edge cases in collision detection."""
        ship_transform = ship.get_component('transform')
        ship_collision = ship.get_component('collision')
        asteroid_transform = asteroid.get_component('transform')
        asteroid_collision = asteroid.get_component('collision')
        
        # Test edge of collision radius
        ship_transform.position = pygame.Vector2(100, 100)
        asteroid_transform.position = pygame.Vector2(
            ship_transform.position.x + ship_collision.radius + asteroid_collision.radius + 1,  # Add 1 to ensure no collision
            ship_transform.position.y
        )
        assert not ship_collision.check_collision(asteroid_collision)

class TestBoundaryWrapping:
    def test_horizontal_wrapping(self, ship):
        """Test screen wrapping horizontally."""
        transform = ship.get_component('transform')
        collision = ship.get_component('collision')
        screen_wrap = ship.get_component('screen_wrap')
        
        # Move ship beyond right edge
        transform.position.x = WINDOW_WIDTH + collision.radius
        screen_wrap.update(0.016)  # Add dt parameter
        assert transform.position.x < collision.radius

        # Move ship beyond left edge
        transform.position.x = -collision.radius
        screen_wrap.update(0.016)  # Add dt parameter
        assert transform.position.x > WINDOW_WIDTH - collision.radius

    def test_vertical_wrapping(self, ship):
        """Test screen wrapping vertically."""
        transform = ship.get_component('transform')
        collision = ship.get_component('collision')
        screen_wrap = ship.get_component('screen_wrap')
        
        # Move ship beyond bottom edge
        transform.position.y = WINDOW_HEIGHT + collision.radius
        screen_wrap.update(0.016)  # Add dt parameter
        assert transform.position.y < collision.radius

        # Move ship beyond top edge
        transform.position.y = -collision.radius
        screen_wrap.update(0.016)  # Add dt parameter
        assert transform.position.y > WINDOW_HEIGHT - collision.radius

    def test_diagonal_wrapping(self, ship):
        """Test screen wrapping diagonally."""
        transform = ship.get_component('transform')
        collision = ship.get_component('collision')
        screen_wrap = ship.get_component('screen_wrap')
        
        # Move ship beyond both edges
        transform.position = pygame.Vector2(
            WINDOW_WIDTH + collision.radius,
            WINDOW_HEIGHT + collision.radius
        )
        screen_wrap.update(0.016)  # Add dt parameter
        assert transform.position.x < collision.radius
        assert transform.position.y < collision.radius

        # Move ship beyond both edges in the other direction
        transform.position = pygame.Vector2(
            -collision.radius,
            -collision.radius
        )
        screen_wrap.update(0.016)  # Add dt parameter
        assert transform.position.x > WINDOW_WIDTH - collision.radius
        assert transform.position.y > WINDOW_HEIGHT - collision.radius
