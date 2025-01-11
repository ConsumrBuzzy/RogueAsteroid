"""Particle entity for visual effects."""
import pygame
from src.core.entities.base import Entity, TransformComponent
from src.core.entities.components import ParticleComponent, PhysicsComponent

class Particle(Entity):
    """A particle entity for visual effects."""
    
    def __init__(self, game, lifetime: float = 0.5, color: tuple = (255, 200, 50)):
        """Initialize the particle.
        
        Args:
            game: The game instance
            lifetime: How long the particle lives in seconds
            color: RGB color tuple for the particle
        """
        super().__init__(game)
        
        # Add transform component at origin (will be positioned later)
        self.add_component(TransformComponent, 0, 0)
        
        # Add physics component with no friction
        physics = self.add_component(PhysicsComponent)
        physics.friction = 0.0  # No friction for particles
        physics.mass = 0.1  # Very light
        physics.max_speed = 1000.0  # Allow high speeds
        
        # Add particle component for rendering and lifetime
        particle = self.add_component(ParticleComponent, lifetime=lifetime, color=color)
        particle.size = 2.0  # Default size in pixels 