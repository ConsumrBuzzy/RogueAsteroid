"""Particle component module."""
import pygame
from typing import Optional
from .base import Component

class ParticleComponent(Component):
    """Component for particle effects."""
    def __init__(self, entity):
        super().__init__(entity)
        self.lifetime = 1.0  # Total lifetime in seconds
        self.time_alive = 0.0  # Current time alive in seconds
        self.color = pygame.Color(255, 255, 255)  # Particle color
        self.alpha = 255  # Current alpha value
        self.start_size = 1.0  # Initial size
        self.end_size = 0.0  # Final size before death
        self.fade_speed = 1.0  # How quickly the particle fades
    
    def update(self, dt: float) -> None:
        """Update particle state."""
        self.time_alive += dt
        
        # Calculate life progress (0 to 1)
        life_progress = self.time_alive / self.lifetime if self.lifetime > 0 else 1
        
        # Update alpha for fade effect
        self.alpha = max(0, 255 * (1 - life_progress * self.fade_speed))
        
        # Update size
        current_size = self.start_size + (self.end_size - self.start_size) * life_progress
        
        # Disable particle when lifetime is exceeded
        if self.time_alive >= self.lifetime:
            self.disable()
    
    def reset(self) -> None:
        """Reset particle to initial state."""
        self.time_alive = 0.0
        self.alpha = 255
        self.enable() 