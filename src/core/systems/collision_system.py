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
        """Handle collision between two asteroids."""
        physics1 = asteroid1.get_component(PhysicsComponent)
        physics2 = asteroid2.get_component(PhysicsComponent)
        transform1 = asteroid1.get_component(TransformComponent)
        transform2 = asteroid2.get_component(TransformComponent)
        
        if not (physics1 and physics2 and transform1 and transform2):
            return False
            
        # First separate the asteroids
        overlap = combined_radius - distance
        separation = normal * overlap
        transform1.position -= separation * 0.6  # Move them apart more aggressively
        transform2.position += separation * 0.6
        
        # Get velocities and masses
        vel1 = pygame.Vector2(physics1.velocity)
        vel2 = pygame.Vector2(physics2.velocity)
        mass1 = ASTEROID_SIZES[asteroid1.size]['mass']
        mass2 = ASTEROID_SIZES[asteroid2.size]['mass']
        
        # Calculate relative velocity
        rel_vel = vel1 - vel2
        vel_along_normal = rel_vel.dot(normal)
        
        # Only resolve if objects are moving toward each other
        if vel_along_normal > 0:
            return False
            
        # Calculate impulse
        restitution = 0.8  # Bouncy collisions
        j = -(1 + restitution) * vel_along_normal
        j /= (1/mass1 + 1/mass2)
        
        # Apply impulse
        impulse = normal * j
        physics1.velocity = vel1 + (impulse / mass1)
        physics2.velocity = vel2 - (impulse / mass2)
        
        # Calculate spin based on collision
        tangent = pygame.Vector2(-normal.y, normal.x)
        spin_factor = 0.3  # Reduced spin factor
        physics1.angular_velocity = rel_vel.dot(tangent) * spin_factor
        physics2.angular_velocity = -rel_vel.dot(tangent) * spin_factor
        
        return True 