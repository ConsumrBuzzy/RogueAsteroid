"""Entity factory service for creating and managing game entities."""
from typing import Dict, Type, Optional, List
from ..entity.entity import Entity

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
        
    def create_entity(self, type_name: str, **kwargs) -> Optional[Entity]:
        """Create a new entity or reuse a pooled one.
        
        Args:
            type_name: Type of entity to create
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
            entity.enable()
            print(f"Reusing pooled entity of type {type_name}")
        else:
            # Create new entity
            entity_class = self._entity_types[type_name]
            entity = entity_class()
            print(f"Created new entity of type {type_name}")
            
        # Initialize entity
        entity.initialize()
        self._active_entities.append(entity)
        return entity
        
    def remove_entity(self, entity: Entity) -> None:
        """Remove an entity and return it to the pool.
        
        Args:
            entity: Entity to remove
        """
        if entity in self._active_entities:
            entity.disable()
            self._active_entities.remove(entity)
            
            # Add to pool if entity type is registered
            for type_name, entity_class in self._entity_types.items():
                if isinstance(entity, entity_class):
                    self._entity_pools[type_name].append(entity)
                    print(f"Entity returned to pool: {type_name}")
                    break
                    
    def clear_all(self) -> None:
        """Clear all entities and pools."""
        # Destroy all active entities
        for entity in list(self._active_entities):
            entity.destroy()
        self._active_entities.clear()
        
        # Clear all pools
        for pool in self._entity_pools.values():
            for entity in pool:
                entity.destroy()
            pool.clear()
            
        print("Cleared all entities and pools")
        
    def update(self, dt: float) -> None:
        """Update all active entities.
        
        Args:
            dt: Delta time in seconds
        """
        for entity in list(self._active_entities):
            entity.update(dt)
            
    def cleanup(self) -> None:
        """Clean up the service."""
        self.clear_all()
        self._entity_types.clear()
        self._entity_pools.clear()
        print("EntityFactoryService cleaned up") 