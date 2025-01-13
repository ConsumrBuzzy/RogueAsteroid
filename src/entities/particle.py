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
    
    def __init__(self, game, lifetime: float = 0.5, color: tuple = (255, 200, 50), size: float = 2.0):
        """Initialize the particle.
        
        Args:
            game: The game instance
            lifetime: How long the particle should exist in seconds
            color: RGB color tuple for the particle
            size: Size of the particle in pixels
        """
        super().__init__(game)
        
        # Store initial lifetime
        self.initial_lifetime = lifetime
        
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
        half_size = size / 2
        render.vertices = [
            (-half_size, -half_size),
            (half_size, -half_size),
            (half_size, half_size),
            (-half_size, half_size)
        ]  # Square shape for particle
        render.color = color[:3]  # Ensure only RGB values
        render.point_size = size  # Size in pixels
        render.alpha = 255  # Start fully opaque
        
        # Add particle component for lifetime management
        particle = self.add_component(ParticleComponent)
        particle.lifetime = lifetime
        
    def update(self, dt: float) -> None:
        """Update particle state."""
        super().update(dt)
        
        # Update particle fade
        particle = self.get_component(ParticleComponent)
        render = self.get_component(RenderComponent)
        if particle and render:
            # Update lifetime
            particle.time_alive += dt
            
            # Calculate fade based on lifetime
            life_progress = particle.time_alive / self.initial_lifetime
            render.alpha = max(0, int(255 * (1.0 - life_progress)))
            
            # Remove particle if lifetime is over
            if particle.time_alive >= self.initial_lifetime:
                self.game.entity_manager.remove_entity(self)
        
    def destroy(self):
        """Remove the particle from the game."""
        if self in self.game.entity_manager.entities:
            self.game.entity_manager.remove_entity(self) 