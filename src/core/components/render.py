"""Render component for handling entity visualization."""
from typing import List, Tuple, Optional
import math
import pygame
from .component import Component

class RenderComponent(Component):
    """Component for managing entity rendering.
    
    Provides:
    - Shape definition and drawing
    - Color management
    - Visibility control
    - Transform integration
    - Debug visualization
    """
    
    def __init__(self, entity, vertices: List[Tuple[float, float]], color: Tuple[int, int, int],
                 line_width: int = 1, alpha: int = 255):
        """Initialize render component.
        
        Args:
            entity: Entity this component belongs to
            vertices: List of (x, y) vertex coordinates defining the shape
            color: RGB color tuple (0-255 for each component)
            line_width: Width of lines when drawing (default: 1)
            alpha: Transparency value (0-255, default: 255)
        """
        super().__init__(entity)
        self.vertices = vertices
        self.color = color
        self.line_width = line_width
        self.alpha = alpha
        self.visible = True
        self._transformed_vertices: List[Tuple[float, float]] = []
        
        print(f"RenderComponent initialized with {len(vertices)} vertices, color={color}")
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the entity on the screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        if not self.enabled or not self.visible:
            return
            
        # Get transform component for position and rotation
        transform = self.get_sibling_component('TransformComponent')
        if not transform:
            return
            
        # Update transformed vertices based on entity transform
        self._update_transformed_vertices(transform)
        
        # Draw the shape
        if len(self._transformed_vertices) >= 2:
            if self.alpha < 255:
                # Create a temporary surface for alpha blending
                temp_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                pygame.draw.lines(
                    temp_surface,
                    (*self.color, self.alpha),
                    True,  # closed polygon
                    self._transformed_vertices,
                    self.line_width
                )
                screen.blit(temp_surface, (0, 0))
            else:
                # Direct drawing for fully opaque shapes
                pygame.draw.lines(
                    screen,
                    self.color,
                    True,  # closed polygon
                    self._transformed_vertices,
                    self.line_width
                )
    
    def _update_transformed_vertices(self, transform) -> None:
        """Update vertex positions based on entity transform.
        
        Args:
            transform: TransformComponent instance
        """
        self._transformed_vertices = []
        angle_rad = math.radians(transform.rotation)
        cos_rot = math.cos(angle_rad)
        sin_rot = math.sin(angle_rad)
        
        for vx, vy in self.vertices:
            # Scale
            scaled_x = vx * transform.scale
            scaled_y = vy * transform.scale
            
            # Rotate
            rotated_x = scaled_x * cos_rot - scaled_y * sin_rot
            rotated_y = scaled_x * sin_rot + scaled_y * cos_rot
            
            # Translate
            final_x = rotated_x + transform.x
            final_y = rotated_y + transform.y
            
            self._transformed_vertices.append((final_x, final_y))
    
    def set_color(self, color: Tuple[int, int, int]) -> None:
        """Set the render color.
        
        Args:
            color: RGB color tuple (0-255 for each component)
        """
        self.color = color
    
    def set_alpha(self, alpha: int) -> None:
        """Set transparency value.
        
        Args:
            alpha: Transparency value (0-255)
        """
        self.alpha = max(0, min(255, alpha))
    
    def set_vertices(self, vertices: List[Tuple[float, float]]) -> None:
        """Set new vertices for the shape.
        
        Args:
            vertices: List of (x, y) vertex coordinates
        """
        self.vertices = vertices
        print(f"Updated shape to {len(vertices)} vertices")
    
    def show(self) -> None:
        """Make the entity visible."""
        self.visible = True
    
    def hide(self) -> None:
        """Make the entity invisible."""
        self.visible = False 