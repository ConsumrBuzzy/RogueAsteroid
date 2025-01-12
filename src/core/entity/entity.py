"""Base entity class for game objects."""
from typing import Dict, Type, Optional, TypeVar, Generic
from uuid import uuid4

from ..components.component import Component

T = TypeVar('T', bound=Component)

class Entity:
    """Base class for all game entities.
    
    Provides:
    - Component management
    - Lifecycle hooks
    - Unique identification
    - Debug support
    """
    
    def __init__(self):
        """Initialize the entity."""
        self.id = str(uuid4())
        self._components: Dict[Type[Component], Component] = {}
        self._initialized = False
        self._enabled = True
        
    def add_component(self, component: Component) -> None:
        """Add a component to the entity.
        
        Args:
            component: Component to add
            
        Raises:
            ValueError: If component type already exists
        """
        component_type = type(component)
        if component_type in self._components:
            raise ValueError(f"Entity already has component of type {component_type.__name__}")
            
        self._components[component_type] = component
        if self._initialized:
            component.initialize()
            
    def remove_component(self, component_type: Type[Component]) -> None:
        """Remove a component from the entity.
        
        Args:
            component_type: Type of component to remove
        """
        if component := self._components.get(component_type):
            component.destroy()
            del self._components[component_type]
            
    def get_component(self, component_type: Type[T]) -> Optional[T]:
        """Get a component by type.
        
        Args:
            component_type: Type of component to get
            
        Returns:
            Component instance or None if not found
        """
        return self._components.get(component_type)
        
    def has_component(self, component_type: Type[Component]) -> bool:
        """Check if entity has a component type.
        
        Args:
            component_type: Type of component to check
            
        Returns:
            True if entity has component
        """
        return component_type in self._components
        
    def initialize(self) -> None:
        """Initialize the entity and its components."""
        if not self._initialized:
            for component in self._components.values():
                component.initialize()
            self._initialized = True
            
    def destroy(self) -> None:
        """Destroy the entity and its components."""
        for component in list(self._components.values()):
            self.remove_component(type(component))
        self._initialized = False
        self._enabled = False
        
    def enable(self) -> None:
        """Enable the entity and its components."""
        if not self._enabled:
            self._enabled = True
            for component in self._components.values():
                component.enable()
                
    def disable(self) -> None:
        """Disable the entity and its components."""
        if self._enabled:
            self._enabled = False
            for component in self._components.values():
                component.disable()
                
    def update(self, dt: float) -> None:
        """Update the entity and its components.
        
        Args:
            dt: Delta time in seconds
        """
        if self._enabled:
            for component in self._components.values():
                component.update(dt)
                
    @property
    def enabled(self) -> bool:
        """Check if entity is enabled.
        
        Returns:
            True if entity is enabled
        """
        return self._enabled 