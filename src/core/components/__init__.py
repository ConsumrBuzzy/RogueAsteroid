"""Component system initialization and management."""
from typing import Dict, Type, Optional
from .component import Component

class ComponentRegistry:
    """Registry for managing game components.
    
    Provides:
    - Component type registration
    - Component instance creation
    - Type validation
    - Error handling
    """
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the component registry."""
        if self._initialized:
            return
            
        self._components: Dict[str, Type[Component]] = {}
        self._initialized = True
        print("ComponentRegistry initialized")
        
    def register_component(self, type_name: str, component_class: Type[Component]) -> None:
        """Register a component type.
        
        Args:
            type_name: Name to register the type under
            component_class: Component class to register
            
        Raises:
            ValueError: If type_name is already registered
        """
        if type_name in self._components:
            print(f"Warning: Overwriting existing component type {type_name}")
        self._components[type_name] = component_class
        print(f"Registered component type '{type_name}'")
        
    def create_component(self, type_name: str, **kwargs) -> Optional[Component]:
        """Create a component instance.
        
        Args:
            type_name: Type of component to create
            **kwargs: Arguments to pass to component constructor
            
        Returns:
            Created component instance or None if type not found
            
        Raises:
            KeyError: If type_name is not registered
        """
        if type_name not in self._components:
            raise KeyError(f"Unknown component type: {type_name}")
            
        component_class = self._components[type_name]
        return component_class(**kwargs)
        
    def get_component_type(self, type_name: str) -> Optional[Type[Component]]:
        """Get a component type by name.
        
        Args:
            type_name: Name of component type
            
        Returns:
            Component class or None if not found
        """
        return self._components.get(type_name)
        
    def has_component_type(self, type_name: str) -> bool:
        """Check if a component type is registered.
        
        Args:
            type_name: Name of component type
            
        Returns:
            True if type is registered
        """
        return type_name in self._components
        
    def get_registered_types(self) -> list[str]:
        """Get list of registered component types.
        
        Returns:
            List of registered type names
        """
        return list(self._components.keys())
        
    def clear(self) -> None:
        """Clear all registered component types."""
        self._components.clear()
        print("Component registry cleared") 