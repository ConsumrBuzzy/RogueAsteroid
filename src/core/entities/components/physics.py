"""Physics component module."""
import pygame
from .base import Component
from .transform import TransformComponent

class PhysicsComponent(Component):
    """Component for physics simulation."""
    def __init__(self, entity):
        super().__init__(entity)
        self.mass = 1.0
        self.max_speed = 500.0
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)
        self.angular_velocity = 0.0
        self.friction = 0.0
        self.gravity = pygame.Vector2(0, 0)
    
    def apply_force(self, force: pygame.Vector2) -> None:
        """Apply a force to the entity."""
        self.acceleration += force / self.mass
    
    def apply_impulse(self, impulse: pygame.Vector2) -> None:
        """Apply an instantaneous force."""
        self.velocity += impulse / self.mass
    
    def update(self, dt: float) -> None:
        """Update physics state."""
        transform = self.entity.get_component(TransformComponent)
        if not transform:
            return
        
        # Update velocity
        self.velocity += (self.acceleration + self.gravity) * dt
        
        # Apply friction
        if self.friction > 0:
            friction_force = -self.velocity * self.friction
            self.velocity += friction_force * dt
        
        # Enforce speed limit
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)
        
        # Update transform
        transform.position += self.velocity * dt
        transform.rotation += self.angular_velocity * dt
        
        # Reset acceleration
        self.acceleration.x = 0
        self.acceleration.y = 0 