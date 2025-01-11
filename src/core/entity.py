import numpy as np
from typing import Tuple, List

class Entity:
    """Base class for all game entities."""
    
    def __init__(self, x: float, y: float):
        # Transform
        self.position = np.array([x, y], dtype=float)
        self.velocity = np.array([0.0, 0.0], dtype=float)
        self.rotation = 0.0  # degrees
        
        # Collision
        self.radius = 1.0  # for circle collision
        self.active = True
        
        # Rendering
        self.color = (255, 255, 255)  # default white
        self.vertices: List[Tuple[float, float]] = []
    
    def update(self, dt: float) -> None:
        """Update entity state."""
        # Update position based on velocity
        self.position += self.velocity * dt
        
        # Screen wrapping
        self.wrap_position()
    
    def wrap_position(self) -> None:
        """Wrap entity position around screen edges."""
        from .constants import WINDOW_WIDTH, WINDOW_HEIGHT
        
        self.position[0] %= WINDOW_WIDTH
        self.position[1] %= WINDOW_HEIGHT
    
    def collides_with(self, other: 'Entity') -> bool:
        """Simple circle collision check."""
        distance = np.linalg.norm(self.position - other.position)
        return distance < (self.radius + other.radius)
    
    def get_direction(self) -> np.ndarray:
        """Get entity's forward direction vector."""
        angle_rad = np.radians(self.rotation)
        return np.array([np.cos(angle_rad), np.sin(angle_rad)])
    
    def draw(self, surface) -> None:
        """Draw entity on the surface."""
        import pygame
        if self.vertices:
            # Transform vertices based on position and rotation
            transformed_vertices = self._get_transformed_vertices()
            pygame.draw.lines(surface, self.color, True, transformed_vertices)
    
    def _get_transformed_vertices(self) -> List[Tuple[float, float]]:
        """Get vertices transformed by entity's position and rotation."""
        angle_rad = np.radians(self.rotation)
        cos_rot = np.cos(angle_rad)
        sin_rot = np.sin(angle_rad)
        
        transformed = []
        for x, y in self.vertices:
            # Rotate
            rx = x * cos_rot - y * sin_rot
            ry = x * sin_rot + y * cos_rot
            # Translate
            rx += self.position[0]
            ry += self.position[1]
            transformed.append((rx, ry))
            
        return transformed 