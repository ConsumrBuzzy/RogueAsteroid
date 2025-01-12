"""Physics component for entity movement."""
import pygame
from src.core.entities.base import Component, Entity, TransformComponent

class PhysicsComponent(Component):
    """Component for physics-based movement."""
    
    def __init__(self, entity: Entity):
        """Initialize the physics component.
        
        Args:
            entity: The entity this component belongs to
        """
        super().__init__(entity)
        self.max_speed = 0.0
        self.friction = 0.0
        self.acceleration = pygame.Vector2(0.0, 0.0)
    
    def initialize(self) -> None:
        """Initialize the component."""
        # Verify we have a transform component
        if not self.entity.get_component(TransformComponent):
            raise RuntimeError("PhysicsComponent requires TransformComponent")
    
    def update(self, dt: float) -> None:
        """Update physics state.
        
        Args:
            dt: Time delta in seconds
        """
        if not self.active:
            return
            
        transform = self.entity.get_component(TransformComponent)
        if not transform:
            return
            
        # Apply acceleration
        transform.velocity += self.acceleration * dt
        
        # Apply friction
        if transform.velocity.length() > 0:
            friction = transform.velocity.normalize() * -self.friction * dt
            transform.velocity += friction
        
        # Clamp speed
        if self.max_speed > 0 and transform.velocity.length() > self.max_speed:
            transform.velocity.scale_to_length(self.max_speed)
            
        # Reset acceleration
        self.acceleration = pygame.Vector2(0.0, 0.0)
    
    def apply_force(self, force: pygame.Vector2) -> None:
        """Apply a force to the entity.
        
        Args:
            force: Force vector to apply
        """
        self.acceleration += force 