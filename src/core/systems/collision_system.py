"""Collision handling system."""
import pygame
import random
from typing import List, Tuple
from src.core.entities.base import Entity
from src.core.entities.components import (
    TransformComponent,
    CollisionComponent,
    PhysicsComponent
)
from src.entities.ship import Ship
from src.entities.bullet import Bullet
from src.entities.asteroid import Asteroid
from src.core.constants import ASTEROID_SIZES
import math

class CollisionSystem:
    """Handles collision detection and response between entities."""
    
    def __init__(self, game):
        """Initialize the collision system."""
        self.game = game
    
    def update(self):
        """Update collision detection and response."""
        # Get all entities with collision components
        collidable_entities = [
            entity for entity in self.game.entities 
            if entity.get_component(CollisionComponent)
        ]
        
        # Check each pair of entities
        for i, entity1 in enumerate(collidable_entities):
            for entity2 in collidable_entities[i + 1:]:
                if self._check_and_handle_collision(entity1, entity2):
                    # If collision was handled, move to next entity1
                    break
    
    def _check_and_handle_collision(self, entity1: Entity, entity2: Entity) -> bool:
        """Check and handle collision between two entities."""
        # Get required components
        collision1 = entity1.get_component(CollisionComponent)
        collision2 = entity2.get_component(CollisionComponent)
        transform1 = entity1.get_component(TransformComponent)
        transform2 = entity2.get_component(TransformComponent)
        
        if not (collision1 and collision2 and transform1 and transform2):
            return False
            
        # Get positions
        pos1 = pygame.Vector2(transform1.position)
        pos2 = pygame.Vector2(transform2.position)
        
        # Calculate distance and check for collision
        distance = pos1.distance_to(pos2)
        combined_radius = collision1.radius + collision2.radius
        
        if distance >= combined_radius:
            return False
            
        # Calculate collision normal
        diff = pos2 - pos1
        if diff.length() > 0:
            normal = diff.normalize()
        else:
            normal = pygame.Vector2(1, 0)
        
        # Handle different collision types
        if isinstance(entity1, Ship) and isinstance(entity2, Asteroid):
            return self._handle_ship_asteroid_collision(entity1, entity2)
        elif isinstance(entity1, Asteroid) and isinstance(entity2, Ship):
            return self._handle_ship_asteroid_collision(entity2, entity1)
        elif isinstance(entity1, Bullet) and isinstance(entity2, Asteroid):
            return self._handle_bullet_asteroid_collision(entity1, entity2)
        elif isinstance(entity1, Asteroid) and isinstance(entity2, Bullet):
            return self._handle_bullet_asteroid_collision(entity2, entity1)
        elif isinstance(entity1, Asteroid) and isinstance(entity2, Asteroid):
            return self._handle_asteroid_asteroid_collision(
                entity1, entity2, pos1, pos2, distance, combined_radius, normal
            )
        
        return False
    
    def _handle_ship_asteroid_collision(self, ship: Ship, asteroid: Asteroid) -> bool:
        """Handle collision between ship and asteroid."""
        if not ship.invulnerable:
            print("Ship hit by asteroid")
            self.game.lose_life()
            transform = ship.get_component(TransformComponent)
            if transform:
                self.game.create_explosion(
                    transform.position.x,
                    transform.position.y,
                    'medium'
                )
            return True
        return False
    
    def _handle_bullet_asteroid_collision(self, bullet: Bullet, asteroid: Asteroid) -> bool:
        """Handle collision between bullet and asteroid."""
        print(f"Bullet hit asteroid size {asteroid.size}")
        
        # Award points
        points = {'large': 3, 'medium': 2, 'small': 1}
        self.game.scoring.add_points(points[asteroid.size])
        
        # Create explosion
        transform = asteroid.get_component(TransformComponent)
        if transform:
            self.game.create_explosion(
                transform.position.x,
                transform.position.y,
                asteroid.size
            )
        
        # Split asteroid
        pieces = asteroid.split()
        for piece in pieces:
            self.game.asteroids.append(piece)
            self.game.entities.append(piece)
        
        # Remove bullet and asteroid
        self.game.remove_entity(bullet)
        self.game.remove_entity(asteroid)
        return True
    
    def _handle_asteroid_asteroid_collision(
        self,
        asteroid1: Asteroid,
        asteroid2: Asteroid,
        pos1: pygame.Vector2,
        pos2: pygame.Vector2,
        distance: float,
        combined_radius: float,
        normal: pygame.Vector2
    ) -> bool:
        """Handle collision between two asteroids using arcade-style physics."""
        physics1 = asteroid1.get_component(PhysicsComponent)
        physics2 = asteroid2.get_component(PhysicsComponent)
        transform1 = asteroid1.get_component(TransformComponent)
        transform2 = asteroid2.get_component(TransformComponent)
        
        if not (physics1 and physics2 and transform1 and transform2):
            return False
            
        # Simple separation - move both asteroids apart equally
        overlap = combined_radius - distance
        if overlap > 0:
            separation = normal * overlap * 0.5  # Split separation equally
            transform1.position -= separation
            transform2.position += separation
            
            # Get velocities
            vel1 = pygame.Vector2(physics1.velocity)
            vel2 = pygame.Vector2(physics2.velocity)
            
            # Simple velocity exchange - more arcade-like
            # Exchange the velocity components along the collision normal
            v1_normal = normal * vel1.dot(normal)
            v2_normal = normal * vel2.dot(normal)
            
            # Keep tangential velocities
            v1_tangent = vel1 - v1_normal
            v2_tangent = vel2 - v2_normal
            
            # Exchange normal components with slight energy loss
            damping = 0.9  # Slight energy loss on collision
            physics1.velocity = v1_tangent + v2_normal * damping
            physics2.velocity = v2_tangent + v1_normal * damping
            
            # Add a small random spin - classic arcade feel
            physics1.angular_velocity = random.uniform(-math.pi/4, math.pi/4)
            physics2.angular_velocity = random.uniform(-math.pi/4, math.pi/4)
            
            return True
                
        return False 