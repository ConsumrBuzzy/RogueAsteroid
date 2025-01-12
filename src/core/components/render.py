"""Component for rendering entities."""
from typing import List, Tuple, TYPE_CHECKING
import pygame
import numpy as np

from ..entity.entity import Entity
from .transform import TransformComponent

if TYPE_CHECKING:
    from ..game import Game

class RenderComponent:
    """Component for rendering entities.
    
    Manages the visual representation of an entity, including:
    - Shape definition (vertices)
    - Color management
    - Visibility control
    - Transform integration
    """
    
    def __init__(self, entity: Entity, vertices: List[Tuple[float, float]] = None, 
                 color: Tuple[int, int, int] = (255, 255, 255), line_width: int = 1,
                 alpha: int = 255) -> None:
        """Initialize the render component.
        
        Args:
            entity: The entity this component belongs to
            vertices: List of (x,y) vertex coordinates defining the shape
            color: RGB color tuple
            line_width: Width of lines when drawing
            alpha: Transparency value (0-255)
        """
        self._entity = entity
        self._vertices = vertices or [(0, 0)]
        self._color = color
        self._line_width = line_width
        self._alpha = alpha
        self._visible = True
        self._transform = None
        self._transformed_vertices = None
        self._update_transform()
        
    @property
    def entity(self) -> Entity:
        """Get the entity this component belongs to."""
        return self._entity
        
    @property
    def visible(self) -> bool:
        """Get visibility state."""
        return self._visible
        
    @visible.setter
    def visible(self, value: bool) -> None:
        """Set visibility state.
        
        Args:
            value: New visibility state
        """
        self._visible = value
        
    @property
    def color(self) -> Tuple[int, int, int]:
        """Get current color."""
        return self._color
        
    @color.setter
    def color(self, value: Tuple[int, int, int]) -> None:
        """Set color.
        
        Args:
            value: New RGB color tuple
        """
        self._color = value
        
    @property
    def vertices(self) -> List[Tuple[float, float]]:
        """Get shape vertices."""
        return self._vertices
        
    @vertices.setter
    def vertices(self, value: List[Tuple[float, float]]) -> None:
        """Set shape vertices.
        
        Args:
            value: New vertex list
        """
        self._vertices = value
        self._update_transform()
        
    def _update_transform(self) -> None:
        """Update transformed vertices based on entity transform."""
        self._transform = self.entity.get_component('transform')
        if self._transform and self._vertices:
            # Convert vertices to numpy array for transformation
            vertices = np.array(self._vertices)
            
            # Get transform properties
            pos = self._transform.position
            angle = np.radians(self._transform.rotation)
            
            # Create rotation matrix
            c, s = np.cos(angle), np.sin(angle)
            R = np.array([[c, -s], [s, c]])
            
            # Apply rotation and translation
            self._transformed_vertices = vertices @ R + pos
            
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the entity on the screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        if not self._visible:
            return
            
        self._update_transform()
        if self._transformed_vertices is not None:
            # Convert vertices to screen coordinates
            points = [(int(x), int(y)) for x, y in self._transformed_vertices]
            
            # Draw shape
            if len(points) > 2:
                pygame.draw.polygon(screen, self._color, points, self._line_width)
            elif len(points) == 2:
                pygame.draw.line(screen, self._color, points[0], points[1], self._line_width)
            else:
                pygame.draw.circle(screen, self._color, points[0], self._line_width)
                
    def update(self, dt: float) -> None:
        """Update the render component.
        
        Args:
            dt: Delta time in seconds
        """
        pass  # Rendering is handled in draw() 