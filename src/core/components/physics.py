"""Physics component for entity movement."""
import pygame
from src.core.components.base import Component
from typing import Any

class PhysicsComponent(Component):
    """Component for physics-based movement."""
    
    def __init__(self, entity: Any, max_speed: float = 0.0, friction: float = 0.0):
        """Initialize the physics component.
        
        Args:
            entity: The entity this component belongs to
            max_speed: Maximum speed limit (0 for no limit)
            friction: Friction coefficient
        """
        super().__init__(entity)
        self.max_speed = max_speed
        self.friction = friction
        self.acceleration = pygame.Vector2(0.0, 0.0)
    
    def update(self, dt: float) -> None:
        """Update physics state.
        
        Args:
            dt: Time delta in seconds
        """
        if not self.active:
            return
            
        transform = self.entity.get_component('TransformComponent')
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