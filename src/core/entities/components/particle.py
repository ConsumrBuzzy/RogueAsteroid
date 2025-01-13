"""Particle component module."""
from .base import Component
from .transform import TransformComponent
from .render import RenderComponent
import pygame

class ParticleComponent(Component):
    """Component for managing particle lifetime and alpha."""
    
    def __init__(self, entity):
        super().__init__(entity)
        self.lifetime = 1.0  # Total lifetime in seconds
        self.time_alive = 0.0  # Current time alive in seconds
        
    def update(self, dt: float) -> None:
        """Update particle state."""
        super().update(dt)
        
        # Update lifetime
        self.time_alive += dt
        
        # Update alpha in render component
        render = self.entity.get_component(RenderComponent)
        if render:
            life_progress = self.time_alive / self.lifetime
            render.alpha = max(0, int(255 * (1.0 - life_progress)))
        
        # Remove particle if lifetime is over
        if self.time_alive >= self.lifetime:
            if self.entity in self.entity.game.entities:
                self.entity.game.entities.remove(self.entity) 
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the particle effect.
        
        Args:
            screen: The pygame surface to draw on
        """
        # Particles are drawn through their RenderComponent
        pass 