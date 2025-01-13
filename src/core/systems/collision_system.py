"""Collision system for handling entity collisions."""
import pygame
import random
import math
from src.entities.asteroid import Asteroid
from src.entities.bullet import Bullet
from src.entities.ship import Ship
from src.core.entities.components import (
    TransformComponent,
    PhysicsComponent,
    CollisionComponent
)

class CollisionSystem:
    """System for handling collisions between entities."""
    
    def __init__(self, game):
        self.game = game
    
    def update(self) -> None:
        """Update collision checks for all entities."""
        # Check collisions between all pairs of entities
        entities = self.game.entities
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                entity1 = entities[i]
                entity2 = entities[j]
                if self._check_and_handle_collision(entity1, entity2):
                    # If collision was handled, continue to next entity
                    break
    
    def _check_and_handle_collision(self, entity1, entity2) -> bool:
        """Check and handle collision between two entities.
        
        Returns:
            bool: True if collision was handled, False otherwise
        """
        # Skip if either entity doesn't have collision component
        collision1 = entity1.get_component(CollisionComponent)
        collision2 = entity2.get_component(CollisionComponent)
        if not collision1 or not collision2:
            return False
            
        # Get positions
        transform1 = entity1.get_component(TransformComponent)
        transform2 = entity2.get_component(TransformComponent)
        if not transform1 or not transform2:
            return False
            
        # Calculate distance between entities
        distance = transform1.position.distance_to(transform2.position)
        
        # Check if collision occurred
        if distance < collision1.radius + collision2.radius:
            # Handle based on entity types
            if isinstance(entity1, Ship) and isinstance(entity2, Asteroid):
                return self._handle_ship_asteroid_collision(entity1, entity2)
            elif isinstance(entity2, Ship) and isinstance(entity1, Asteroid):
                return self._handle_ship_asteroid_collision(entity2, entity1)
            elif isinstance(entity1, Bullet) and isinstance(entity2, Asteroid):
                return self._handle_bullet_asteroid_collision(entity1, entity2)
            elif isinstance(entity2, Bullet) and isinstance(entity1, Asteroid):
                return self._handle_bullet_asteroid_collision(entity2, entity1)
            elif isinstance(entity1, Asteroid) and isinstance(entity2, Asteroid):
                return self._handle_asteroid_asteroid_collision(entity1, entity2)
        
        return False
    
    def _handle_ship_asteroid_collision(self, ship: Ship, asteroid: Asteroid) -> bool:
        """Handle collision between ship and asteroid."""
        if not ship.invulnerable:
            # Create large explosion effect for ship collision
            transform = ship.get_component(TransformComponent)
            if transform:
                self.game.create_explosion(transform.position, 'large')
            
            # Lose a life and respawn
            self.game.lose_life()
            return True
        return False
    
    def _handle_bullet_asteroid_collision(self, bullet: Bullet, asteroid: Asteroid) -> bool:
        """Handle collision between bullet and asteroid."""
        # Get positions for explosion effect
        transform = asteroid.get_component(TransformComponent)
        if transform:
            # Create explosion based on asteroid size
            self.game.create_explosion(transform.position, asteroid.size)
        
        # Split or destroy asteroid
        asteroid.split()
        
        # Remove bullet
        if bullet in self.game.bullets:
            self.game.bullets.remove(bullet)
        if bullet in self.game.entities:
            self.game.entities.remove(bullet)
            
        return True
    
    def _handle_asteroid_asteroid_collision(self, asteroid1: Asteroid, asteroid2: Asteroid) -> bool:
        """Handle collision between two asteroids."""
        # Get components
        transform1 = asteroid1.get_component(TransformComponent)
        transform2 = asteroid2.get_component(TransformComponent)
        physics1 = asteroid1.get_component(PhysicsComponent)
        physics2 = asteroid2.get_component(PhysicsComponent)
        
        if not transform1 or not transform2 or not physics1 or not physics2:
            return False
            
        # Calculate collision normal
        normal = transform2.position - transform1.position
        if normal.length() == 0:
            # If positions are identical, use a random normal
            normal = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        normal = normal.normalize()
        
        # Calculate relative velocity
        relative_velocity = physics2.velocity - physics1.velocity
        
        # Calculate impulse
        restitution = 0.8  # Bounciness
        impulse = -(1 + restitution) * relative_velocity.dot(normal)
        impulse /= (1/physics1.mass + 1/physics2.mass)
        
        # Apply impulse
        physics1.velocity -= (impulse / physics1.mass) * normal
        physics2.velocity += (impulse / physics2.mass) * normal
        
        # Add some random spin
        physics1.angular_velocity += random.uniform(-30, 30)
        physics2.angular_velocity += random.uniform(-30, 30)
        
        return True 