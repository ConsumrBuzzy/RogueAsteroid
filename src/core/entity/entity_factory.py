"""Factory for creating and managing game entities."""
from typing import Dict, Type, List, Optional, Any
from .entity import Entity

class EntityFactory:
    """Factory for creating and managing game entities.
    
    Provides:
    - Centralized entity creation
    - Entity type registration
    - Entity pooling
    - Lifecycle management
    """
    
    def __init__(self, game):
        """Initialize the entity factory.
        
        Args:
            game: Reference to main game instance
        """
        self.game = game
        self._entity_types: Dict[str, Type[Entity]] = {}
        self._entities: List[Entity] = []
        self._entity_pools: Dict[str, List[Entity]] = {}
        
        # Debug info
        print("EntityFactory initialized")
    
    def register_entity_type(self, type_name: str, entity_class: Type[Entity]) -> None:
        """Register a new entity type.
        
        Args:
            type_name: Name to register the entity type under
            entity_class: Entity class to register
        """
        if type_name in self._entity_types:
            print(f"Warning: Overwriting existing entity type {type_name}")
        self._entity_types[type_name] = entity_class
        print(f"Registered entity type: {type_name}")
    
    def create_entity(self, type_name: str, x: float = 0, y: float = 0, **kwargs) -> Optional[Entity]:
        """Create a new entity of the specified type.
        
        Args:
            type_name: Type of entity to create
            x: Initial x position
            y: Initial y position
            **kwargs: Additional arguments for entity initialization
            
        Returns:
            Created entity instance or None if type not found
        """
        # Check if we have a pooled entity available
        if type_name in self._entity_pools and self._entity_pools[type_name]:
            entity = self._entity_pools[type_name].pop()
            entity.x = x
            entity.y = y
            entity.is_active = True
            entity.is_destroyed = False
            print(f"Reused pooled entity of type {type_name}")
            return entity
        
        # Create new entity if type exists
        if type_name in self._entity_types:
            entity = self._entity_types[type_name](self.game, x, y, **kwargs)
            self._entities.append(entity)
            print(f"Created new entity of type {type_name}")
            return entity
        
        print(f"Error: Unknown entity type {type_name}")
        return None
    
    def remove_entity(self, entity: Entity, pool: bool = True) -> None:
        """Remove an entity from the game.
        
        Args:
            entity: Entity to remove
            pool: Whether to pool the entity for reuse
        """
        if entity not in self._entities:
            return
            
        entity.destroy()
        self._entities.remove(entity)
        
        # Add to pool if enabled
        if pool:
            entity_type = type(entity).__name__
            if entity_type not in self._entity_pools:
                self._entity_pools[entity_type] = []
            self._entity_pools[entity_type].append(entity)
            print(f"Added entity to {entity_type} pool")
        
        print(f"Removed entity {entity.id}")
    
    def update(self, dt: float) -> None:
        """Update all active entities.
        
        Args:
            dt: Delta time in seconds
        """
        # Update entities and track which need removal
        to_remove = []
        for entity in self._entities:
            if entity.is_destroyed:
                to_remove.append(entity)
            elif entity.is_active:
                entity.update(dt)
        
        # Remove destroyed entities
        for entity in to_remove:
            self.remove_entity(entity)
    
    def clear_all(self) -> None:
        """Remove all entities from the game."""
        for entity in self._entities[:]:
            self.remove_entity(entity, pool=False)
        self._entity_pools.clear()
        print("Cleared all entities") 