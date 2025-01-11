"""Asteroid entity implementation."""
import pygame
import numpy as np
from typing import List, Tuple, Optional
from random import uniform, randint
from src.core.entity import Entity
from src.core.constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WHITE
)

class Asteroid(Entity):
    """Asteroid entity that can split into smaller pieces."""
    
    # Size configurations
    SIZES = {
        'large': {'radius': 40.0, 'points': 20, 'splits': 2},
        'medium': {'radius': 20.0, 'points': 50, 'splits': 2},
        'small': {'radius': 10.0, 'points': 100, 'splits': 0}
    }
    
    def __init__(self, x: float, y: float, size: str = 'large', velocity: Optional[np.ndarray] = None):
        super().__init__(x, y)
        
        # Asteroid properties
        self.size_category = size
        self.radius = self.SIZES[size]['radius']
        self.points = self.SIZES[size]['points']
        self.color = WHITE
        
        # Generate random polygon shape
        self.vertices = self._generate_shape()
        
        # Set random velocity if none provided
        if velocity is None:
            speed = uniform(50.0, 100.0)
            angle = uniform(0, 2 * np.pi)
            self.velocity = np.array([
                speed * np.cos(angle),
                speed * np.sin(angle)
            ])
        else:
            self.velocity = velocity
        
        # Random rotation
        self.rotation_speed = uniform(-90, 90)  # degrees per second
    
    def _generate_shape(self) -> List[Tuple[float, float]]:
        """Generate a random polygon shape for the asteroid."""
        num_vertices = randint(8, 12)
        vertices = []
        
        for i in range(num_vertices):
            angle = (i / num_vertices) * 2 * np.pi
            # Add some randomness to the radius
            radius_variance = uniform(0.8, 1.2)
            x = np.cos(angle) * self.radius * radius_variance
            y = np.sin(angle) * self.radius * radius_variance
            vertices.append((x, y))
        
        return vertices
    
    def update(self, dt: float) -> None:
        """Update asteroid position and rotation."""
        # Update rotation
        self.rotation += self.rotation_speed * dt
        
        # Update position
        super().update(dt)
    
    def split(self) -> List['Asteroid']:
        """Split asteroid into smaller pieces."""
        if self.size_category == 'small':
            return []
        
        # Determine next size
        next_size = 'medium' if self.size_category == 'large' else 'small'
        
        # Create new asteroids
        new_asteroids = []
        num_splits = self.SIZES[self.size_category]['splits']
        
        for _ in range(num_splits):
            # Calculate new velocity (perpendicular to current)
            perp_angle = uniform(-np.pi/4, np.pi/4)
            speed_mult = uniform(1.2, 1.5)
            
            velocity_norm = np.linalg.norm(self.velocity)
            new_velocity = np.array([
                -self.velocity[1],
                self.velocity[0]
            ])
            new_velocity = new_velocity / np.linalg.norm(new_velocity) * velocity_norm * speed_mult
            
            # Rotate velocity
            cos_angle = np.cos(perp_angle)
            sin_angle = np.sin(perp_angle)
            rotated_velocity = np.array([
                new_velocity[0] * cos_angle - new_velocity[1] * sin_angle,
                new_velocity[0] * sin_angle + new_velocity[1] * cos_angle
            ])
            
            # Create new asteroid
            new_asteroid = Asteroid(
                self.position[0],
                self.position[1],
                next_size,
                rotated_velocity
            )
            new_asteroids.append(new_asteroid)
        
        return new_asteroids 