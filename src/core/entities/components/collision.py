"""Collision component module."""
import pygame
from typing import Optional
from .base import Component
from .transform import TransformComponent

class CollisionComponent(Component):
    """Component for handling collisions.
    
    Manages collision detection between entities using circular collision bounds.
    """
    
    def __init__(self, entity, radius: float = 10.0):
        super().__init__(entity)
        self._radius = radius
        self._active = True
    
    @property
    def radius(self) -> float:
        """Get the collision radius."""
        return self._radius
        
    @radius.setter
    def radius(self, value: float) -> None:
        """Set the collision radius."""
        self._radius = value
    
    @property
    def active(self) -> bool:
        """Get the collision active state."""
        return self._active
        
    @active.setter
    def active(self, value: bool) -> None:
        """Set the collision active state."""
        self._active = value
    
    def check_collision(self, other: 'CollisionComponent') -> bool:
        """Check for collision with another collision component.
        
        Args:
            other: The other collision component to check against.
            
        Returns:
            True if the components are colliding, False otherwise.
        """
        if not (self._active and other._active):
            return False
            
        transform = self.entity.get_component(TransformComponent)
        other_transform = other.entity.get_component(TransformComponent)
        
        if not (transform and other_transform):
            return False
            
        distance = transform.position.distance_to(other_transform.position)
        return distance <= (self._radius + other._radius)
    
    def get_collision_normal(self, other: 'CollisionComponent') -> Optional[pygame.Vector2]:
        """Get the collision normal vector between this and another component.
        
        Args:
            other: The other collision component.
            
        Returns:
            Normalized vector pointing from other to this component, or None if not colliding.
        """
        if not self.check_collision(other):
            return None
            
        transform = self.entity.get_component(TransformComponent)
        other_transform = other.entity.get_component(TransformComponent)
        
        if not (transform and other_transform):
            return None
            
        # Get vector from other to this
        normal = transform.position - other_transform.position
        if normal.length() > 0:
            normal.normalize_ip()
            return normal
        return pygame.Vector2(1, 0)  # Default direction if positions are identical
    
    def get_collision_depth(self, other: 'CollisionComponent') -> float:
        """Get the overlap depth between this and another component.
        
        Args:
            other: The other collision component.
            
        Returns:
            The overlap depth, or 0 if not colliding.
        """
        if not self.check_collision(other):
            return 0.0
            
        transform = self.entity.get_component(TransformComponent)
        other_transform = other.entity.get_component(TransformComponent)
        
        if not (transform and other_transform):
            return 0.0
            
        distance = transform.position.distance_to(other_transform.position)
        return self._radius + other._radius - distance 