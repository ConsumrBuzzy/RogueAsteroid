"""Particle entity for visual effects."""
from src.core.entities.base import Entity, TransformComponent, RenderComponent
from src.core.entities.components import PhysicsComponent, ParticleComponent

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
        
        # Add transform at origin
        self.add_component(TransformComponent, 0, 0)
        
        # Add physics with no friction and very light mass
        physics = self.add_component(PhysicsComponent)
        physics.friction = 0.0
        physics.mass = 0.1
        physics.max_speed = 1000.0  # Allow high speeds for particles
        
        # Add particle component with lifetime and color
        particle = self.add_component(ParticleComponent)
        particle.lifetime = lifetime
        particle.color = color
        particle.size = 2.0  # Default size in pixels 