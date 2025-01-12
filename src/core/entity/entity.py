"""Base entity class for game objects."""
import logging
from typing import Dict, Type, Optional
import pygame

from ..components import ComponentRegistry

logger = logging.getLogger(__name__)

class Entity:
    """Base class for all game entities."""
    
    def __init__(self):
        """Initialize the entity."""
        self.id: int = 0  # Set by EntityManagerService
        self._components: Dict[str, object] = {}
        self._registry = ComponentRegistry()
        self.active = True
        
    def add_component(self, component_type: Type, *args, **kwargs) -> None:
        """Add a component to the entity.
        
        Args:
            component_type: The type of component to add
            *args: Positional arguments for component initialization
            **kwargs: Keyword arguments for component initialization
        """
        try:
            component = component_type(*args, **kwargs)
            component_name = component_type.__name__
            self._components[component_name] = component
            logger.debug(f"Added component {component_name} to entity {self.id}")
        except Exception as e:
            logger.error(f"Failed to add component {component_type.__name__} to entity {self.id}: {e}", exc_info=True)
            raise
            
    def remove_component(self, component_type: Type) -> None:
        """Remove a component from the entity.
        
        Args:
            component_type: The type of component to remove
        """
        component_name = component_type.__name__
        if component_name in self._components:
            try:
                component = self._components[component_name]
                if hasattr(component, 'cleanup'):
                    component.cleanup()
                del self._components[component_name]
                logger.debug(f"Removed component {component_name} from entity {self.id}")
            except Exception as e:
                logger.error(f"Failed to remove component {component_name} from entity {self.id}: {e}", exc_info=True)
                raise
                
    def get_component(self, component_type: Type) -> Optional[object]:
        """Get a component by type.
        
        Args:
            component_type: The type of component to get
            
        Returns:
            The component if found, None otherwise
        """
        return self._components.get(component_type.__name__)
        
    def has_component(self, component_type: Type) -> bool:
        """Check if the entity has a component.
        
        Args:
            component_type: The type of component to check for
            
        Returns:
            True if the entity has the component, False otherwise
        """
        return component_type.__name__ in self._components
        
    def update(self, dt: float) -> None:
        """Update the entity and its components.
        
        Args:
            dt: Time elapsed since last update in seconds
        """
        if not self.active:
            return
            
        for component in self._components.values():
            if hasattr(component, 'update'):
                try:
                    component.update(dt)
                except Exception as e:
                    logger.error(f"Error updating component {type(component).__name__} of entity {self.id}: {e}", exc_info=True)
                    
    def draw(self) -> None:
        """Draw the entity using its render component."""
        if not self.active:
            return
            
        render_component = self.get_component('RenderComponent')
        if render_component and hasattr(render_component, 'draw'):
            try:
                render_component.draw()
            except Exception as e:
                logger.error(f"Error drawing entity {self.id}: {e}", exc_info=True)
                
    def cleanup(self) -> None:
        """Clean up the entity and its components."""
        logger.debug(f"Cleaning up entity {self.id}")
        for component_name, component in self._components.items():
            if hasattr(component, 'cleanup'):
                try:
                    component.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up component {component_name} of entity {self.id}: {e}", exc_info=True)
        self._components.clear()
        self.active = False 