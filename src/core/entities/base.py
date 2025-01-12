"""Base entity classes for the game engine."""
from typing import Dict, Type, Any, Optional
from src.core.components.base import Component

class Entity:
    """Base class for all game entities."""
    
    def __init__(self):
        """Initialize the entity."""
        self.components: Dict[str, Component] = {}
        self.active = True
    
    def add_component(self, component_type: str, *args, **kwargs) -> Optional[Component]:
        """Add a component to the entity.
        
        Args:
            component_type: Type name of component to add
            *args: Positional arguments for component constructor
            **kwargs: Keyword arguments for component constructor
            
        Returns:
            The created component or None if creation failed
        """
        from src.core.components import ComponentRegistry
        registry = ComponentRegistry()
        component = registry.create_component(component_type, self, *args, **kwargs)
        if component:
            self.components[component_type] = component
        return component
    
    def get_component(self, component_type: str) -> Optional[Component]:
        """Get a component by type.
        
        Args:
            component_type: Type name of component to get
            
        Returns:
            The component if found, None otherwise
        """
        return self.components.get(component_type)
    
    def remove_component(self, component_type: str) -> None:
        """Remove a component by type.
        
        Args:
            component_type: Type name of component to remove
        """
        if component_type in self.components:
            self.components[component_type].cleanup()
            del self.components[component_type]
    
    def update(self, dt: float) -> None:
        """Update all components.
        
        Args:
            dt: Time elapsed since last update in seconds
        """
        for component in self.components.values():
            if component.active:
                component.update(dt)
    
    def draw(self, surface: Any) -> None:
        """Draw all components.
        
        Args:
            surface: Surface to draw on
        """
        for component in self.components.values():
            if component.active:
                component.draw(surface)
    
    def cleanup(self) -> None:
        """Clean up the entity and all its components."""
        for component in self.components.values():
            component.cleanup()
        self.components.clear() 