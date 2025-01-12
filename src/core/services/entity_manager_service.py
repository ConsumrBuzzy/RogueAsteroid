"""Entity management service for handling game entities."""
import logging
from typing import Dict, List, Optional
import pygame

from ..entity import Entity
from . import ServiceManager
from ..components import ComponentRegistry
from ..constants import SCREEN_WIDTH, SCREEN_HEIGHT

logger = logging.getLogger(__name__)

class EntityManagerService:
    """Service for managing game entities."""
    
    def __init__(self, service_manager: 'ServiceManager'):
        """Initialize the entity manager.
        
        Args:
            service_manager: ServiceManager instance for accessing other services
        """
        logger.info("Initializing EntityManagerService")
        self._service_manager = service_manager
        self._entities: Dict[int, Entity] = {}
        self._entities_to_add: List[Entity] = []
        self._entities_to_remove: List[int] = []
        self._next_entity_id = 1
        self._registry = ComponentRegistry()
        
    def create_entity(self, entity_class: type, *args, **kwargs) -> Entity:
        """Create a new entity.
        
        Args:
            entity_class: The class of entity to create
            *args: Positional arguments for entity initialization
            **kwargs: Keyword arguments for entity initialization
            
        Returns:
            The created entity instance
        """
        entity = entity_class(*args, **kwargs)
        entity.id = self._next_entity_id
        self._next_entity_id += 1
        self._entities_to_add.append(entity)
        return entity
        
    def remove_entity(self, entity_id: int) -> None:
        """Mark an entity for removal.
        
        Args:
            entity_id: ID of the entity to remove
        """
        self._entities_to_remove.append(entity_id)
        
    def get_entity(self, entity_id: int) -> Optional[Entity]:
        """Get an entity by ID.
        
        Args:
            entity_id: ID of the entity to get
            
        Returns:
            The entity if found, None otherwise
        """
        return self._entities.get(entity_id)
        
    def update(self, dt: float) -> None:
        """Update all entities.
        
        Args:
            dt: Time elapsed since last update in seconds
        """
        # Add new entities
        for entity in self._entities_to_add:
            self._entities[entity.id] = entity
        self._entities_to_add.clear()
        
        # Update existing entities
        for entity in list(self._entities.values()):
            try:
                entity.update(dt)
            except Exception as e:
                logger.error(f"Error updating entity {entity.id}: {e}", exc_info=True)
                self.remove_entity(entity.id)
                
        # Remove marked entities
        for entity_id in self._entities_to_remove:
            if entity_id in self._entities:
                try:
                    self._entities[entity_id].cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up entity {entity_id}: {e}", exc_info=True)
                del self._entities[entity_id]
        self._entities_to_remove.clear()
        
    def draw(self) -> None:
        """Draw all entities."""
        for entity in self._entities.values():
            try:
                entity.draw()
            except Exception as e:
                logger.error(f"Error drawing entity {entity.id}: {e}", exc_info=True)
                
    def cleanup(self) -> None:
        """Clean up all entities."""
        logger.info("Cleaning up EntityManagerService")
        for entity in self._entities.values():
            try:
                entity.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up entity {entity.id}: {e}", exc_info=True)
        self._entities.clear()
        self._entities_to_add.clear()
        self._entities_to_remove.clear() 