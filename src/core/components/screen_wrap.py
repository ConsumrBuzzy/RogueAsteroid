"""Screen wrap component for keeping entities in bounds."""
from typing import Tuple
import pygame
from src.core.entities.base import Component, Entity, TransformComponent

class ScreenWrapComponent(Component):
    """Component for wrapping entities around screen edges."""
    
    def __init__(self, entity: Entity, screen_size: Tuple[int, int]):
        """Initialize the screen wrap component.
        
        Args:
            entity: The entity this component belongs to
            screen_size: (width, height) of the screen
        """
        super().__init__(entity)
        self.screen_width, self.screen_height = screen_size
        self.margin = 0  # Extra margin before wrapping
    
    def initialize(self) -> None:
        """Initialize the component."""
        # Verify we have a transform component
        if not self.entity.get_component(TransformComponent):
            raise RuntimeError("ScreenWrapComponent requires TransformComponent")
    
    def update(self, dt: float) -> None:
        """Update screen wrapping.
        
        Args:
            dt: Time delta in seconds
        """
        if not self.active:
            return
            
        transform = self.entity.get_component(TransformComponent)
        if not transform:
            return
            
        # Wrap position around screen edges
        x = transform.position.x
        y = transform.position.y
        
        # Wrap horizontally
        if x < -self.margin:
            x = self.screen_width + self.margin
        elif x > self.screen_width + self.margin:
            x = -self.margin
            
        # Wrap vertically
        if y < -self.margin:
            y = self.screen_height + self.margin
        elif y > self.screen_height + self.margin:
            y = -self.margin
            
        # Update position if changed
        if x != transform.position.x or y != transform.position.y:
            transform.position = pygame.Vector2(x, y)
    
    def set_margin(self, margin: float) -> None:
        """Set the wrap margin.
        
        Args:
            margin: Distance beyond screen edge before wrapping
        """
        self.margin = margin 