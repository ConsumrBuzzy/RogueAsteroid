"""Render component module."""
import pygame
import math
from typing import List, Tuple
from .base import Component
from .transform import TransformComponent

class RenderComponent(Component):
    """Component for rendering entities.
    
    Handles the visual representation of an entity, including its shape, color,
    and visibility state. Supports both line and polygon rendering.
    """
    
    def __init__(self, entity):
        super().__init__(entity)
        self._color = (255, 255, 255)  # Default white
        self._vertices: List[Tuple[float, float]] = []
        self._visible = True
    
    @property
    def color(self) -> Tuple[int, int, int]:
        """Get the current color."""
        return self._color
        
    @color.setter
    def color(self, value: Tuple[int, int, int]) -> None:
        """Set the current color."""
        self._color = value
    
    @property
    def vertices(self) -> List[Tuple[float, float]]:
        """Get the current vertices."""
        return self._vertices
        
    @vertices.setter
    def vertices(self, value: List[Tuple[float, float]]) -> None:
        """Set the current vertices."""
        self._vertices = value
    
    @property
    def visible(self) -> bool:
        """Get the current visibility state."""
        return self._visible
        
    @visible.setter
    def visible(self, value: bool) -> None:
        """Set the current visibility state."""
        self._visible = value
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the entity on the screen.
        
        Args:
            screen: The pygame surface to draw on.
        """
        if not self._visible or len(self._vertices) < 2:
            return
            
        transform = self.entity.get_component(TransformComponent)
        if not transform:
            return
            
        # Convert local vertices to world space
        world_vertices = self._get_world_vertices(transform)
        
        # Draw lines between vertices
        if len(world_vertices) == 2:  # Line (for bullets)
            pygame.draw.line(screen, self._color, world_vertices[0], world_vertices[1])
        else:  # Polygon (for ship and asteroids)
            pygame.draw.polygon(screen, self._color, world_vertices, 1)
    
    def _get_world_vertices(self, transform: TransformComponent) -> List[Tuple[float, float]]:
        """Convert local vertices to world space.
        
        Args:
            transform: The transform component to use for the conversion.
            
        Returns:
            List of vertices in world space.
        """
        world_vertices = []
        rotation_rad = math.radians(transform.rotation)
        cos_rot = math.cos(rotation_rad)
        sin_rot = math.sin(rotation_rad)
        
        for vertex in self._vertices:
            # Rotate vertex
            x = vertex[0] * cos_rot - vertex[1] * sin_rot
            y = vertex[0] * sin_rot + vertex[1] * cos_rot
            
            # Translate to world position
            world_x = x + transform.position.x
            world_y = y + transform.position.y
            world_vertices.append((world_x, world_y))
            
        return world_vertices 