"""Physics component module."""
import pygame
from .base import Component
from .transform import TransformComponent

class PhysicsComponent(Component):
    """Component for physics simulation."""
    def __init__(self, entity, velocity=None, friction=0.0):
        """Initialize the physics component.
        
        Args:
            entity: The entity this component belongs to
            velocity: Initial velocity vector (pygame.Vector2)
            friction: Friction coefficient (0.0 to 1.0)
        """
        self.entity = entity
        self.velocity = velocity or pygame.Vector2(0, 0)
        self.friction = friction
        self.paused = False  # Add paused state
    
    def update(self, dt):
        """Update the physics component.
        
        Args:
            dt: Time delta in seconds
        """
        if self.paused:  # Skip update if paused
            return
            
        # Get transform component
        transform = self.entity.get_component(TransformComponent)
        if not transform:
            return
        
        # Apply friction
        if self.friction > 0 and self.velocity.length() > 0:
            friction_force = self.velocity.normalize() * -self.friction
            self.velocity += friction_force * dt
            
            # Stop if velocity is very small
            if self.velocity.length() < 0.1:
                self.velocity = pygame.Vector2(0, 0)
        
        # Update position
        transform.position += self.velocity * dt 