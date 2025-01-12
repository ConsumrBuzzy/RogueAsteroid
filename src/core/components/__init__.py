"""Component system initialization and registry."""
from typing import Dict, Type, Optional
from .component import Component

class ComponentRegistry:
    """Central registry for managing game components.
    
    Provides:
    - Component type registration
    - Component creation
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
        """Initialize component registry."""
        if self._initialized:
            return
            
        self._components: Dict[str, Type[Component]] = {}
        self._initialized = True
        print("ComponentRegistry initialized")
    
    def register_component(self, name: str, component_class: Type[Component]) -> None:
        """Register a component type.
        
        Args:
            name: Unique name for the component type
            component_class: Component class to register
        
        Raises:
            ValueError: If component_class doesn't inherit from Component
            Warning: If overwriting existing component type
        """
        # Validate component class
        if not issubclass(component_class, Component):
            raise ValueError(f"Component class {component_class.__name__} must inherit from Component")
            
        # Warn if overwriting
        if name in self._components:
            print(f"Warning: Overwriting existing component type '{name}'")
            
        self._components[name] = component_class
        print(f"Registered component type '{name}'")
    
    def create_component(self, name: str, entity, **kwargs) -> Optional[Component]:
        """Create a component instance.
        
        Args:
            name: Name of component type to create
            entity: Entity to attach component to
            **kwargs: Additional arguments for component initialization
            
        Returns:
            Created component instance or None if type not found
            
        Raises:
            Exception: If component creation fails
        """
        if name not in self._components:
            print(f"Warning: Unknown component type '{name}'")
            return None
            
        try:
            component = self._components[name](entity, **kwargs)
            print(f"Created component '{name}' for entity {entity.id}")
            return component
        except Exception as e:
            print(f"Error creating component '{name}': {e}")
            raise
    
    def get_component_type(self, name: str) -> Optional[Type[Component]]:
        """Get a registered component type.
        
        Args:
            name: Name of component type
            
        Returns:
            Component class or None if not found
        """
        return self._components.get(name)
    
    def has_component_type(self, name: str) -> bool:
        """Check if a component type is registered.
        
        Args:
            name: Name of component type
            
        Returns:
            True if component type exists
        """
        return name in self._components
    
    def clear_registry(self) -> None:
        """Clear all registered component types."""
        self._components.clear()
        print("Component registry cleared") 