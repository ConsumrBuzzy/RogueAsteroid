"""Collision service for game-wide collision management."""
from typing import List, Dict, Optional, Tuple, Set
import math
from ..entity import Entity

class CollisionLayer:
    """Enumeration of collision layers."""
    NONE = 0
    PLAYER = 1
    ENEMY = 2
    PROJECTILE = 4
    PICKUP = 8
    ALL = 15  # All bits set

class CollisionService:
    """Service for game-wide collision management.
    
    Provides:
    - Collision detection
    - Layer-based filtering
    - Spatial partitioning
    - Collision response
    - Debug visualization
    """
    
    def __init__(self):
        """Initialize the collision service."""
        self._entities: List[Entity] = []
        self._collision_pairs: Set[Tuple[Entity, Entity]] = set()
        print("CollisionService initialized")
        
    def register_entity(self, entity: Entity) -> None:
        """Register an entity for collision detection.
        
        Args:
            entity: Entity to register
        """
        if entity not in self._entities:
            self._entities.append(entity)
            print(f"Registered entity {entity.id} for collision detection")
            
    def unregister_entity(self, entity: Entity) -> None:
        """Unregister an entity from collision detection.
        
        Args:
            entity: Entity to unregister
        """
        if entity in self._entities:
            self._entities.remove(entity)
            print(f"Unregistered entity {entity.id} from collision detection")
            
    def update(self) -> None:
        """Update collision detection for all registered entities."""
        self._collision_pairs.clear()
        
        # Check collisions between all entities
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
                if self._check_collision(entity1, entity2):
                    self._collision_pairs.add((entity1, entity2))
                    collision1.on_collision(entity2)
                    collision2.on_collision(entity1)
                    
    def _check_collision(self, entity1: Entity, entity2: Entity) -> bool:
        """Check for collision between two entities.
        
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
        
    def get_colliding_pairs(self) -> Set[Tuple[Entity, Entity]]:
        """Get all currently colliding entity pairs.
        
        Returns:
            Set of tuples containing colliding entity pairs
        """
        return self._collision_pairs
        
    def clear(self) -> None:
        """Clear all registered entities."""
        self._entities.clear()
        self._collision_pairs.clear()
        print("Collision service cleared") 