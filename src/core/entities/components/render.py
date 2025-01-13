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
        self._alpha = 255  # Transparency (0-255)
        self._point_size = 1.0  # For particle rendering
    
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
        
    @property
    def alpha(self) -> int:
        """Get the current alpha value."""
        return self._alpha
        
    @alpha.setter
    def alpha(self, value: int) -> None:
        """Set the current alpha value."""
        self._alpha = max(0, min(255, value))
        
    @property
    def point_size(self) -> float:
        """Get the current point size."""
        return self._point_size
        
    @point_size.setter
    def point_size(self, value: float) -> None:
        """Set the current point size."""
        self._point_size = value
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the entity on the screen.
        
        Args:
            screen: The pygame surface to draw on.
        """
        if not self._visible or not self._vertices:
            return
            
        transform = self.entity.get_component(TransformComponent)
        if not transform:
            return
            
        # If it's a particle (single point with size)
        if len(self._vertices) == 1 and self._point_size > 1.0:
            size = int(self._point_size * 2)
            particle_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            
            # Draw particle with alpha
            color_with_alpha = (*self._color, self._alpha)
            pygame.draw.circle(
                particle_surface,
                color_with_alpha,
                (size//2, size//2),
                self._point_size
            )
            
            # Position and draw
            pos = transform.position - pygame.Vector2(size//2, size//2)
            screen.blit(particle_surface, pos)
            return
            
        # Convert local vertices to world space
        world_vertices = self._get_world_vertices(transform)
        
        # Draw with alpha
        color_with_alpha = (*self._color, self._alpha)
        
        # Draw lines between vertices
        if len(world_vertices) == 2:  # Line (for bullets)
            pygame.draw.line(screen, color_with_alpha, world_vertices[0], world_vertices[1])
        else:  # Polygon (for ship and asteroids)
            pygame.draw.polygon(screen, color_with_alpha, world_vertices, 1)
    
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