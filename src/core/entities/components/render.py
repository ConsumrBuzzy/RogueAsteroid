"""Render component for drawing entities."""
import pygame
import math
from .base import Component

class RenderComponent(Component):
    """Component for rendering entities."""
    
    def __init__(self, entity):
        super().__init__(entity)
        self.vertices = []  # List of (x, y) tuples defining shape
        self.color = (255, 255, 255)  # Default white
        self.point_size = 1.0  # Size for point particles
        self.alpha = 255  # Transparency (0-255)
        
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the entity on the surface."""
        if not self.vertices:
            return
            
        # If it's a single point (particle)
        if len(self.vertices) == 1 and self.point_size > 1.0:
            # Create a small surface for the particle
            size = int(self.point_size * 2)
            particle_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            
            # Draw the particle with alpha
            color_with_alpha = (*self.color, self.alpha)
            pygame.draw.circle(
                particle_surface,
                color_with_alpha,
                (size//2, size//2),
                self.point_size
            )
            
            # Get position and blit
            from .transform import TransformComponent
            transform = self.entity.get_component(TransformComponent)
            if transform:
                pos = transform.position - pygame.Vector2(size//2, size//2)
                surface.blit(particle_surface, pos)
        else:
            # Regular polygon drawing
            from .transform import TransformComponent
            transform = self.entity.get_component(TransformComponent)
            if transform:
                # Transform vertices based on entity position and rotation
                transformed_vertices = []
                for x, y in self.vertices:
                    # Rotate point
                    angle_rad = math.radians(transform.rotation)
                    rotated_x = x * math.cos(angle_rad) - y * math.sin(angle_rad)
                    rotated_y = x * math.sin(angle_rad) + y * math.cos(angle_rad)
                    
                    # Translate to position
                    final_x = rotated_x + transform.position.x
                    final_y = rotated_y + transform.position.y
                    transformed_vertices.append((final_x, final_y))
                
                # Draw with alpha
                color_with_alpha = (*self.color, self.alpha)
                pygame.draw.polygon(surface, color_with_alpha, transformed_vertices) 