"""Physics service for game-wide physics and collision management."""
from typing import List, Tuple, Optional
import math
import pygame
from ..entity import Entity

class PhysicsService:
    """Service for game-wide physics calculations.
    
    Provides:
    - Collision detection
    - Physics calculations
    - Spatial partitioning
    - Movement validation
    - Debug support
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize the physics service.
        
        Args:
            screen_width: Width of game screen
            screen_height: Height of game screen
        """
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._entities: List[Entity] = []
        print("PhysicsService initialized")
        
    def register_entity(self, entity: Entity) -> None:
        """Register an entity for physics processing.
        
        Args:
            entity: Entity to register
        """
        if entity not in self._entities:
            self._entities.append(entity)
            print(f"Registered entity {entity.id} for physics")
            
    def unregister_entity(self, entity: Entity) -> None:
        """Unregister an entity from physics processing.
        
        Args:
            entity: Entity to unregister
        """
        if entity in self._entities:
            self._entities.remove(entity)
            print(f"Unregistered entity {entity.id} from physics")
            
    def update(self, dt: float) -> None:
        """Update physics for all registered entities.
        
        Args:
            dt: Delta time in seconds
        """
        # Update physics components
        for entity in self._entities:
            physics = entity.get_component('PhysicsComponent')
            if physics and physics.enabled:
                physics.update(dt)
                
        # Check collisions
        self._check_collisions()
        
    def _check_collisions(self) -> None:
        """Check for collisions between all registered entities."""
        for i in range(len(self._entities)):
            entity1 = self._entities[i]
            collision1 = entity1.get_component('CollisionComponent')
            if not collision1 or not collision1.enabled:
                continue
                
            for j in range(i + 1, len(self._entities)):
                entity2 = self._entities[j]
                collision2 = entity2.get_component('CollisionComponent')
                if not collision2 or not collision2.enabled:
                    continue
                    
                # Check collision masks
                if not (collision1.layer & collision2.mask) or not (collision2.layer & collision1.mask):
                    continue
                    
                # Check actual collision
                if self._check_circle_collision(entity1, entity2):
                    collision1.on_collision(entity2)
                    collision2.on_collision(entity1)
                    
    def _check_circle_collision(self, entity1: Entity, entity2: Entity) -> bool:
        """Check for collision between two entities using circle collision.
        
        Args:
            entity1: First entity to check
            entity2: Second entity to check
            
        Returns:
            True if entities are colliding
        """
        transform1 = entity1.get_component('TransformComponent')
        transform2 = entity2.get_component('TransformComponent')
        collision1 = entity1.get_component('CollisionComponent')
        collision2 = entity2.get_component('CollisionComponent')
        
        if not all([transform1, transform2, collision1, collision2]):
            return False
            
        # Calculate distance between centers
        dx = transform2.x - transform1.x
        dy = transform2.y - transform1.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Check if circles overlap
        return distance < (collision1.radius + collision2.radius)
        
    def wrap_position(self, x: float, y: float) -> Tuple[float, float]:
        """Wrap a position around screen boundaries.
        
        Args:
            x: X coordinate to wrap
            y: Y coordinate to wrap
            
        Returns:
            Tuple of wrapped (x, y) coordinates
        """
        wrapped_x = x % self._screen_width
        wrapped_y = y % self._screen_height
        return wrapped_x, wrapped_y
        
    def calculate_direction(self, angle: float) -> Tuple[float, float]:
        """Calculate direction vector from angle.
        
        Args:
            angle: Angle in radians
            
        Returns:
            Tuple of (x, y) direction vector
        """
        return math.cos(angle), math.sin(angle)
        
    def clear(self) -> None:
        """Clear all registered entities."""
        self._entities.clear()
        print("Physics service cleared") 