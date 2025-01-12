"""Asteroid entity that players must avoid and destroy."""
import pygame
from typing import Tuple
import random
import math

from .base import Entity
from ..components import (
    TransformComponent,
    PhysicsComponent,
    RenderComponent,
    CollisionComponent,
    ScreenWrapComponent
)
from ..constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    ASTEROID_LARGE_SIZE,
    ASTEROID_MEDIUM_SIZE,
    ASTEROID_SMALL_SIZE,
    ASTEROID_LARGE_POINTS,
    ASTEROID_MEDIUM_POINTS,
    ASTEROID_SMALL_POINTS
)

class Asteroid(Entity):
    """Destructible asteroid that splits into smaller pieces."""
    
    def __init__(self, position: Tuple[float, float], size: float, velocity: Tuple[float, float]):
        """Initialize the asteroid.
        
        Args:
            position: Initial (x, y) position
            size: Asteroid size (radius)
            velocity: Initial (vx, vy) velocity
        """
        super().__init__()
        
        # Store size for splitting logic
        self.size = size
        
        # Generate random polygon points for asteroid shape
        num_points = random.randint(8, 12)
        variation = 0.3  # How much points can vary from perfect circle
        points = []
        
        for i in range(num_points):
            angle = (i / num_points) * 2 * math.pi
            distance = size * (1 + random.uniform(-variation, variation))
            x = math.cos(angle) * distance
            y = math.sin(angle) * distance
            points.append((x, y))
            
        # Add required components
        self.add_component(TransformComponent(
            position=position,
            rotation=random.uniform(0, 360),
            scale=(1, 1)
        ))
        
        self.add_component(PhysicsComponent(
            velocity=velocity,
            angular_velocity=random.uniform(-90, 90)  # Random rotation
        ))
        
        self.add_component(RenderComponent(
            color=(150, 150, 150),  # Gray
            points=points
        ))
        
        self.add_component(CollisionComponent(
            radius=size,
            layer="asteroid"
        ))
        
        self.add_component(ScreenWrapComponent(
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT
        ))
        
    def split(self) -> list['Asteroid']:
        """Split asteroid into smaller pieces.
        
        Returns:
            List of new smaller asteroids, or empty list if asteroid is too small
        """
        if self.size == ASTEROID_LARGE_SIZE:
            new_size = ASTEROID_MEDIUM_SIZE
        elif self.size == ASTEROID_MEDIUM_SIZE:
            new_size = ASTEROID_SMALL_SIZE
        else:
            return []  # Too small to split
            
        # Create 2-3 smaller asteroids
        num_pieces = random.randint(2, 3)
        new_asteroids = []
        
        transform = self.get_component(TransformComponent)
        physics = self.get_component(PhysicsComponent)
        
        base_velocity = 30  # Base velocity for new asteroids
        
        for _ in range(num_pieces):
            # Calculate new velocity vector
            angle = random.uniform(0, 2 * math.pi)
            vx = math.cos(angle) * base_velocity
            vy = math.sin(angle) * base_velocity
            
            # Create new asteroid with slight position offset
            offset = random.uniform(-10, 10)
            new_pos = (
                transform.position[0] + offset,
                transform.position[1] + offset
            )
            
            # Add original velocity to maintain momentum
            new_velocity = (
                physics.velocity[0] + vx,
                physics.velocity[1] + vy
            )
            
            new_asteroids.append(Asteroid(new_pos, new_size, new_velocity))
            
        return new_asteroids
        
    @property
    def points(self) -> int:
        """Get points value for destroying this asteroid."""
        if self.size == ASTEROID_LARGE_SIZE:
            return ASTEROID_LARGE_POINTS
        elif self.size == ASTEROID_MEDIUM_SIZE:
            return ASTEROID_MEDIUM_POINTS
        else:
            return ASTEROID_SMALL_POINTS 