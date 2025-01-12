"""Collision component module."""
import pygame
from typing import Optional, Callable, Any
from .base import Component
from .transform import TransformComponent

class CollisionComponent(Component):
    """Component for collision detection."""
    def __init__(self, entity, radius: float = 10.0):
        super().__init__(entity)
        self.radius = radius
        self.tag = ""  # Collision tag for filtering
        self.layer = 0  # Collision layer
        self.group = 0  # Collision group
        self.is_static = False  # Static objects don't move during collision
        self.on_collision: Optional[Callable[[Any], None]] = None
    
    def is_colliding_with(self, other: 'CollisionComponent') -> bool:
        """Check if colliding with another collision component."""
        if not self.enabled or not other.enabled:
            return False
            
        transform = self.entity.get_component(TransformComponent)
        other_transform = other.entity.get_component(TransformComponent)
        
        if not transform or not other_transform:
            return False
        
        # Calculate distance between centers
        distance = transform.position.distance_to(other_transform.position)
        return distance < (self.radius + other.radius) 