"""Unit tests for game entities."""
import unittest
import numpy as np
from src.core.game import Game
from src.entities.ship import Ship
from src.entities.asteroid import Asteroid
from src.entities.bullet import Bullet
from src.core.entities.base import TransformComponent
import pygame

class TestShip(unittest.TestCase):
    """Test cases for Ship entity."""
    
    def setUp(self):
        self.game = Game()
        self.ship = Ship(self.game)
    
    def test_initialization(self):
        """Test ship initialization."""
        self.assertIsNotNone(self.ship.get_component('transform'))
        self.assertIsNotNone(self.ship.get_component('physics'))
        self.assertIsNotNone(self.ship.get_component('render'))
        self.assertIsNotNone(self.ship.get_component('input'))
        self.assertIsNotNone(self.ship.get_component('collision'))
        self.assertIsNotNone(self.ship.get_component('screen_wrap'))
    
    def test_thrust(self):
        """Test ship thrust."""
        game = Game()
        ship = Ship(game)
        transform = ship.get_component("transform")
        initial_velocity = transform.velocity.copy()
        
        ship.thrust()  # Apply thrust
        
        # Velocity should change
        self.assertNotEqual(transform.velocity, initial_velocity)
    
    def test_rotation(self):
        """Test ship rotation."""
        game = Game()
        ship = Ship(game)
        transform = ship.get_component("transform")
        initial_rotation = transform.rotation
        
        ship.rotate_left()  # Rotate counter-clockwise
        
        # Rotation should decrease
        self.assertLess(transform.rotation, initial_rotation)
        
        # Reset rotation
        transform.rotation = initial_rotation
        
        ship.rotate_right()  # Rotate clockwise
        
        # Rotation should increase
        self.assertGreater(transform.rotation, initial_rotation)
    
    def test_shooting(self):
        """Test ship shooting mechanics."""
        initial_entities = len(self.game.entities)
        
        # Shoot
        self.ship._shoot()
        
        # Check that bullet was created
        self.assertEqual(len(self.game.entities), initial_entities + 1)
        self.assertIsInstance(self.game.entities[-1], Bullet)

class TestAsteroid(unittest.TestCase):
    """Test cases for Asteroid entity."""
    
    def setUp(self):
        self.game = Game()
        # Create asteroid with position as Vector2
        self.asteroid = Asteroid(
            self.game,
            'large',
            pygame.Vector2(400, 300)
        )
    
    def test_initialization(self):
        """Test asteroid initialization."""
        self.assertIsNotNone(self.asteroid.get_component('transform'))
        self.assertIsNotNone(self.asteroid.get_component('physics'))
        self.assertIsNotNone(self.asteroid.get_component('render'))
        self.assertIsNotNone(self.asteroid.get_component('collision'))
        self.assertIsNotNone(self.asteroid.get_component('screen_wrap'))
    
    def test_splitting(self):
        """Test asteroid splitting mechanics."""
        # Split large asteroid
        new_asteroids = self.asteroid.split()
        self.assertEqual(len(new_asteroids), 2)
        self.assertEqual(new_asteroids[0].size, 'medium')
        
        # Split medium asteroid
        medium_asteroid = new_asteroids[0]
        new_small_asteroids = medium_asteroid.split()
        self.assertEqual(len(new_small_asteroids), 2)
        self.assertEqual(new_small_asteroids[0].size, 'small')
        
        # Split small asteroid
        small_asteroid = new_small_asteroids[0]
        final_asteroids = small_asteroid.split()
        self.assertEqual(len(final_asteroids), 0)

class TestBullet(unittest.TestCase):
    """Test cases for Bullet entity."""
    
    def setUp(self):
        self.game = Game()
        # Create bullet with direction as Vector2
        self.bullet = Bullet(
            self.game,
            pygame.Vector2(400, 300),  # position
            pygame.Vector2(1.0, 0.0)   # direction
        )
    
    def test_initialization(self):
        """Test bullet initialization."""
        self.assertIsNotNone(self.bullet.get_component('transform'))
        self.assertIsNotNone(self.bullet.get_component('physics'))
        self.assertIsNotNone(self.bullet.get_component('render'))
        self.assertIsNotNone(self.bullet.get_component('collision'))
    
    def test_lifetime(self):
        """Test bullet lifetime mechanics."""
        self.game.entities.append(self.bullet)
        initial_entities = len(self.game.entities)
        
        # Update for longer than lifetime
        self.bullet.update(self.bullet.LIFETIME + 0.1)
        
        # Check that bullet was removed
        self.assertEqual(len(self.game.entities), initial_entities - 1)
    
    def test_movement(self):
        """Test bullet movement."""
        transform = self.bullet.get_component('transform')
        self.assertIsNotNone(transform)
        
        initial_pos = pygame.Vector2(transform.position)
        self.bullet.update(0.1)
        
        # Check that bullet has moved in the right direction
        self.assertGreater(transform.position.x, initial_pos.x)
        self.assertEqual(transform.position.y, initial_pos.y)

if __name__ == '__main__':
    unittest.main() 