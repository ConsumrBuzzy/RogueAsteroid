"""Registry for managing component types and creation."""
from typing import Dict, Type, Optional, Any
from .component import Component

class ComponentRegistry:
    """Registry for managing and creating components.
    
    Provides:
    - Component type registration
    - Component creation
    - Type validation
    - Debug support
    """
    
    def __init__(self):
        """Initialize the component registry."""
        self._component_types: Dict[str, Type[Component]] = {}
        
        # Debug info
        print("ComponentRegistry initialized")
    
    def register_component(self, type_name: str, component_class: Type[Component]) -> None:
        """Register a new component type.
        
        Args:
            type_name: Name to register the component type under
            component_class: Component class to register
        """
        if not issubclass(component_class, Component):
            print(f"Error: {component_class.__name__} must inherit from Component")
            return
            
        if type_name in self._component_types:
            print(f"Warning: Overwriting existing component type {type_name}")
        
        self._component_types[type_name] = component_class
        print(f"Registered component type: {type_name}")
    
    def create_component(self, type_name: str, entity: Any, **kwargs) -> Optional[Component]:
        """Create a new component of the specified type.
        
        Args:
            type_name: Type of component to create
            entity: Entity to attach component to
            **kwargs: Additional arguments for component initialization
            
        Returns:
            Created component instance or None if type not found
        """
        if type_name not in self._component_types:
            print(f"Error: Unknown component type {type_name}")
            return None
            
        component_class = self._component_types[type_name]
        component = component_class(entity, **kwargs)
        print(f"Created component of type {type_name}")
        return component
    
    def get_component_type(self, type_name: str) -> Optional[Type[Component]]:
        """Get a registered component type.
        
        Args:
            type_name: Name of component type to get
            
        Returns:
            Component class if found, None otherwise
        """
        return self._component_types.get(type_name)
    
    def has_component_type(self, type_name: str) -> bool:
        """Check if a component type is registered.
        
        Args:
            type_name: Name of component type to check
            
        Returns:
            True if type exists, False otherwise
        """
        return type_name in self._component_types
    
    def clear_registry(self) -> None:
        """Clear all registered component types."""
        self._component_types.clear()
        print("Cleared component registry") 