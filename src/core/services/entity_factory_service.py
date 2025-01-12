"""Service for creating and managing game entities."""
from typing import Dict, Type, Optional, List
from ..entity import Entity

class EntityFactoryService:
    """Service for creating and managing game entities.
    
    Provides:
    - Entity type registration
    - Centralized entity creation
    - Entity pooling
    - Lifecycle management
    - Debug support
    """
    
    def __init__(self):
        """Initialize the entity factory service."""
        self._entity_types: Dict[str, Type[Entity]] = {}
        self._active_entities: List[Entity] = []
        self._entity_pools: Dict[str, List[Entity]] = {}
        print("EntityFactoryService initialized")
    
    def register_entity_type(self, type_name: str, entity_class: Type[Entity]) -> None:
        """Register a new entity type.
        
        Args:
            type_name: Name to register the type under
            entity_class: Entity class to register
            
        Raises:
            ValueError: If type_name is already registered
        """
        if type_name in self._entity_types:
            print(f"Warning: Overwriting existing entity type {type_name}")
        self._entity_types[type_name] = entity_class
        self._entity_pools[type_name] = []
        print(f"Registered entity type: {type_name}")
    
    def create_entity(self, type_name: str, x: float = 0, y: float = 0, **kwargs) -> Optional[Entity]:
        """Create a new entity or reuse a pooled one.
        
        Args:
            type_name: Type of entity to create
            x: Initial x position
            y: Initial y position
            **kwargs: Additional initialization arguments
            
        Returns:
            Created entity instance or None if type not found
            
        Raises:
            KeyError: If type_name is not registered
        """
        if type_name not in self._entity_types:
            raise KeyError(f"Unknown entity type: {type_name}")
            
        # Try to reuse a pooled entity
        if self._entity_pools[type_name]:
            entity = self._entity_pools[type_name].pop()
            print(f"Reusing pooled entity of type {type_name}")
        else:
            # Create new entity
            entity_class = self._entity_types[type_name]
            entity = entity_class(x=x, y=y, **kwargs)
            print(f"Created new entity of type {type_name}")
            
        self._active_entities.append(entity)
        return entity
    
    def remove_entity(self, entity: Entity, pool: bool = True) -> None:
        """Remove an entity from the game.
        
        Args:
            entity: Entity to remove
            pool: Whether to pool the entity for reuse
        """
        if entity in self._active_entities:
            self._active_entities.remove(entity)
            
            if pool:
                # Find entity type name
                type_name = None
                for name, cls in self._entity_types.items():
                    if isinstance(entity, cls):
                        type_name = name
                        break
                
                if type_name:
                    self._entity_pools[type_name].append(entity)
                    print(f"Pooled entity of type {type_name}")
                else:
                    entity.destroy()
                    print("Entity destroyed (type not found for pooling)")
            else:
                entity.destroy()
                print("Entity destroyed (pooling disabled)")
    
    def update(self, dt: float) -> None:
        """Update all active entities.
        
        Args:
            dt: Delta time in seconds
        """
        # Update in reverse to safely handle removals
        for i in range(len(self._active_entities) - 1, -1, -1):
            entity = self._active_entities[i]
            if entity.is_destroyed:
                self._active_entities.pop(i)
            else:
                entity.update(dt)
    
    def clear_all(self) -> None:
        """Remove all entities and clear pools."""
        for entity in self._active_entities:
            entity.destroy()
        self._active_entities.clear()
        
        for pool in self._entity_pools.values():
            for entity in pool:
                entity.destroy()
            pool.clear()
            
        print("Cleared all entities and pools")
    
    def cleanup(self) -> None:
        """Clean up the service."""
        self.clear_all()
        self._entity_types.clear()
        print("EntityFactoryService cleaned up") 