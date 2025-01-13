"""Particle entity for visual effects."""
from src.core.entities.base import Entity
from src.core.entities.components import (
    TransformComponent,
    RenderComponent,
    PhysicsComponent,
    ParticleComponent
)
import pygame

class Particle(Entity):
    """A particle entity for visual effects."""
    
    def __init__(self, game, lifetime: float = 0.5, color: tuple = (255, 200, 50)):
        """Initialize the particle.
        
        Args:
            game: The game instance
            lifetime: How long the particle should exist in seconds
            color: RGB color tuple for the particle
        """
        super().__init__(game)
        
        # Add transform component
        transform = self.add_component(TransformComponent)
        transform.position = pygame.Vector2(0, 0)  # Will be set by caller
        
        # Add physics with no friction and very light mass
        physics = self.add_component(PhysicsComponent)
        physics.friction = 0.0
        physics.mass = 0.1
        physics.max_speed = 1000.0  # Allow high speeds for particles
        
        # Add render component for visual display
        render = self.add_component(RenderComponent)
        render.vertices = [(0, 0)]  # Single point for particle
        render.color = color
        render.point_size = 2.0  # Size in pixels
        
        # Add particle component for lifetime management
        particle = self.add_component(ParticleComponent)
        particle.lifetime = lifetime
        particle.alpha = 255  # Start fully opaque
        
    def update(self, dt: float) -> None:
        """Update particle state."""
        super().update(dt)
        
        # Update particle fade
        particle = self.get_component(ParticleComponent)
        render = self.get_component(RenderComponent)
        if particle and render:
            # Calculate fade based on lifetime
            life_progress = 1.0 - (particle.lifetime / self.lifetime)
            particle.alpha = int(255 * (1.0 - life_progress))
            render.color = (*render.color[:3], particle.alpha)  # Update alpha
            
            # Remove particle if lifetime is over
            if particle.lifetime <= 0:
                if self in self.game.entities:
                    self.game.entities.remove(self) 