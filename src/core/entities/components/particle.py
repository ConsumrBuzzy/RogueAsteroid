"""Particle component for managing particle effects."""
import pygame
from .base import Component
from .transform import TransformComponent
from .render import RenderComponent

class ParticleComponent(Component):
    """Component for managing particle effects."""
    
    def __init__(self, entity):
        super().__init__(entity)
        self.lifetime = 1.0
        self.time_alive = 0.0
        self.alpha = 255
        
    def update(self, dt: float) -> None:
        """Update particle state."""
        self.time_alive += dt
        
        # Calculate life progress (0 to 1)
        life_progress = self.time_alive / self.lifetime if self.lifetime > 0 else 1
        
        # Update alpha for fade effect
        self.alpha = max(0, int(255 * (1 - life_progress)))
        
        # Update render component alpha
        render = self.entity.get_component(RenderComponent)
        if render:
            render.alpha = self.alpha
        
        # Remove particle when lifetime is exceeded
        if self.time_alive >= self.lifetime:
            self.entity.game.entities.remove(self.entity) 