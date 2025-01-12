"""Particle entity for visual effects."""
from src.core.entity.entity import Entity
from src.core.components.transform import TransformComponent
from src.core.components.render import RenderComponent
from src.core.components.physics import PhysicsComponent
from src.core.components.effect import EffectComponent

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
        
        # Add effect component with lifetime and color
        effect = self.add_component(EffectComponent)
        effect.lifetime = lifetime
        effect.color = color
        effect.size = 2.0  # Default size in pixels 