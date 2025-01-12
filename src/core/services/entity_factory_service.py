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
    
    def __init__(self, service_manager):
        """Initialize the entity factory service.
        
        Args:
            service_manager: ServiceManager instance for accessing services
        """
        self._service_manager = service_manager
        self._entity_types: Dict[str, Type[Entity]] = {}
        self._active_entities: List[Entity] = []
        self._entity_pools: Dict[str, List[Entity]] = {}
        self._pool_limits: Dict[str, int] = {}  # Maximum pool sizes
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
        
    def set_pool_limit(self, type_name: str, limit: int) -> None:
        """Set the maximum size for an entity pool.
        
        Args:
            type_name: Entity type name
            limit: Maximum number of pooled entities
        """
        if limit < 0:
            raise ValueError("Pool limit cannot be negative")
        self._pool_limits[type_name] = limit
        
    def create_entity(self, type_name: str, *args, **kwargs) -> Optional[Entity]:
        """Create or reuse an entity from the pool.
        
        Args:
            type_name: Type of entity to create
            *args: Positional arguments for entity creation
            **kwargs: Keyword arguments for entity creation
            
        Returns:
            New or reused entity instance
            
        Raises:
            ValueError: If entity type not registered
        """
        if type_name not in self._entity_types:
            raise ValueError(f"Entity type not registered: {type_name}")
            
        # Try to reuse from pool
        if type_name in self._entity_pools and self._entity_pools[type_name]:
            entity = self._entity_pools[type_name].pop()
            entity.reset(*args, **kwargs)  # Reset entity state
        else:
            # Create new entity
            entity = self._entity_types[type_name](*args, **kwargs)
            
        self._active_entities.append(entity)
        return entity
        
    def recycle_entity(self, entity: Entity) -> None:
        """Return an entity to its pool for reuse.
        
        Args:
            entity: Entity to recycle
        """
        if entity in self._active_entities:
            self._active_entities.remove(entity)
            
            # Get entity type name
            type_name = entity.__class__.__name__
            
            # Check pool limit
            pool_limit = self._pool_limits.get(type_name, 10)  # Default limit of 10
            if len(self._entity_pools.get(type_name, [])) < pool_limit:
                # Add to pool if under limit
                if type_name not in self._entity_pools:
                    self._entity_pools[type_name] = []
                self._entity_pools[type_name].append(entity)
            else:
                # Let it be garbage collected if pool is full
                print(f"Pool full for {type_name}, letting entity be collected")
        
    def cleanup(self) -> None:
        """Clean up the entity factory service."""
        try:
            # Clear active entities
            for entity in self._active_entities[:]:
                if hasattr(entity, 'cleanup'):
                    entity.cleanup()
            self._active_entities.clear()
            
            # Clear entity pools
            for pool in self._entity_pools.values():
                for entity in pool:
                    if hasattr(entity, 'cleanup'):
                        entity.cleanup()
                pool.clear()
            self._entity_pools.clear()
            
            # Clear type registry
            self._entity_types.clear()
            self._pool_limits.clear()
            
            print("EntityFactoryService cleaned up")
        except Exception as e:
            print(f"Error cleaning up EntityFactoryService: {e}") 