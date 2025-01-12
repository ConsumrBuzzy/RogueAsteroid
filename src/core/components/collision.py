"""Collision component for handling entity collisions."""
from typing import List, Tuple, Optional, Callable
import math
from .component import Component

class CollisionComponent(Component):
    """Component for managing entity collisions.
    
    Provides:
    - Collision shape definition
    - Collision detection
    - Collision response
    - Collision filtering
    - Debug visualization
    """
    
    def __init__(self, entity, radius: float, layer: str = "default",
                 mask: List[str] = None, on_collision: Callable = None):
        """Initialize collision component.
        
        Args:
            entity: Entity this component belongs to
            radius: Collision circle radius
            layer: Collision layer for filtering
            mask: List of layers to collide with (None = all)
            on_collision: Optional callback for collision events
        """
        super().__init__(entity)
        self.radius = radius
        self.layer = layer
        self.mask = mask or ["default"]
        self.on_collision = on_collision
        self.is_trigger = False  # If True, only detects but doesn't resolve
        
        print(f"CollisionComponent initialized with radius={radius}, layer={layer}")
    
    def check_collision(self, other: 'CollisionComponent') -> Optional[Tuple[float, float, float]]:
        """Check for collision with another component.
        
        Args:
            other: Other collision component to check against
            
        Returns:
            Tuple of (overlap, normal_x, normal_y) if colliding, None otherwise
        """
        if not self.enabled or not other.enabled:
            return None
            
        # Check layer masks
        if not self._can_collide_with(other):
            return None
            
        # Get positions from transform components
        self_transform = self.get_sibling_component('TransformComponent')
        other_transform = other.get_sibling_component('TransformComponent')
        
        if not self_transform or not other_transform:
            return None
            
        # Calculate distance and overlap
        dx = other_transform.x - self_transform.x
        dy = other_transform.y - self_transform.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Check for collision
        combined_radius = self.radius + other.radius
        if distance >= combined_radius:
            return None
            
        # Calculate collision normal and overlap
        overlap = combined_radius - distance
        if distance > 0:
            normal_x = dx / distance
            normal_y = dy / distance
        else:
            # Objects are at same position, use arbitrary normal
            normal_x = 1
            normal_y = 0
            
        return (overlap, normal_x, normal_y)
    
    def resolve_collision(self, other: 'CollisionComponent',
                         overlap: float, normal_x: float, normal_y: float) -> None:
        """Resolve collision with another component.
        
        Args:
            other: Other collision component
            overlap: Overlap distance
            normal_x: X component of collision normal
            normal_y: Y component of collision normal
        """
        if self.is_trigger or other.is_trigger:
            return
            
        # Get transforms
        self_transform = self.get_sibling_component('TransformComponent')
        other_transform = other.get_sibling_component('TransformComponent')
        
        if not self_transform or not other_transform:
            return
            
        # Calculate mass ratio (default to equal masses)
        self_physics = self.get_sibling_component('PhysicsComponent')
        other_physics = other.get_sibling_component('PhysicsComponent')
        
        total_mass = 2.0  # Default total mass
        self_mass_ratio = 0.5  # Default to equal mass distribution
        
        if self_physics and other_physics:
            # Use radius as mass approximation if no mass specified
            self_mass = self.radius * self.radius
            other_mass = other.radius * other.radius
            total_mass = self_mass + other_mass
            if total_mass > 0:
                self_mass_ratio = self_mass / total_mass
        
        # Separate objects
        separation = overlap / total_mass
        self_transform.move(
            -normal_x * separation * (1 - self_mass_ratio),
            -normal_y * separation * (1 - self_mass_ratio)
        )
        other_transform.move(
            normal_x * separation * self_mass_ratio,
            normal_y * separation * self_mass_ratio
        )
        
        # Notify collision handlers
        if self.on_collision:
            self.on_collision(other.entity)
    
    def _can_collide_with(self, other: 'CollisionComponent') -> bool:
        """Check if can collide with another component based on layers.
        
        Args:
            other: Other collision component to check against
            
        Returns:
            True if collision is allowed, False otherwise
        """
        return (other.layer in self.mask or "default" in self.mask) and \
               (self.layer in other.mask or "default" in other.mask)
    
    def set_trigger(self, is_trigger: bool) -> None:
        """Set whether this is a trigger collider.
        
        Args:
            is_trigger: If True, only detects but doesn't resolve collisions
        """
        self.is_trigger = is_trigger
        print(f"CollisionComponent trigger mode: {is_trigger}")
    
    def set_collision_mask(self, mask: List[str]) -> None:
        """Set collision mask (which layers to collide with).
        
        Args:
            mask: List of layer names to collide with
        """
        self.mask = mask
        print(f"Updated collision mask: {mask}")
    
    def set_layer(self, layer: str) -> None:
        """Set collision layer.
        
        Args:
            layer: Layer name for this collider
        """
        self.layer = layer
        print(f"Updated collision layer: {layer}")
    
    def set_radius(self, radius: float) -> None:
        """Set collision radius.
        
        Args:
            radius: New collision radius
        """
        self.radius = radius
        print(f"Updated collision radius: {radius}") 