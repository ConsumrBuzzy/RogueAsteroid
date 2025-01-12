"""Transform component module."""
import pygame
from .base import Component

class TransformComponent(Component):
    """Component for position, rotation, and scale."""
    def __init__(self, entity):
        super().__init__(entity)
        self.position = pygame.Vector2(0, 0)
        self.rotation = 0.0  # In degrees
        self.scale = pygame.Vector2(1, 1)
    
    def translate(self, offset: pygame.Vector2) -> None:
        """Move by the given offset."""
        self.position += offset
    
    def rotate(self, angle: float) -> None:
        """Rotate by the given angle in degrees."""
        self.rotation = (self.rotation + angle) % 360
    
    def set_scale(self, scale: pygame.Vector2) -> None:
        """Set the scale vector."""
        self.scale = pygame.Vector2(scale) 