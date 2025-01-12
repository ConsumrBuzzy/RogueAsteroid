"""Component system initialization."""
from typing import Dict, Type, Any, Optional
from src.core.components.base import (
    Component,
    TransformComponent,
    RenderComponent,
    CollisionComponent,
    InputComponent,
    ScreenWrapComponent
)

class ComponentRegistry:
    """Registry for component types."""
    
    _instance = None
    _components: Dict[str, Type[Component]] = {}
    
    def __new__(cls):
        """Create or return the singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_registry()
        return cls._instance
    
    def _init_registry(self) -> None:
        """Initialize the component registry."""
        # Register base components
        self.register_component('TransformComponent', TransformComponent)
        self.register_component('RenderComponent', RenderComponent)
        self.register_component('CollisionComponent', CollisionComponent)
        self.register_component('InputComponent', InputComponent)
        self.register_component('ScreenWrapComponent', ScreenWrapComponent)
    
    def register_component(self, type_name: str, component_type: Type[Component]) -> None:
        """Register a component type.
        
        Args:
            type_name: Name to register the component under
            component_type: The component class to register
        """
        self._components[type_name] = component_type
    
    def create_component(self, type_name: str, entity: Any, *args, **kwargs) -> Optional[Component]:
        """Create a component instance.
        
        Args:
            type_name: Name of the component type to create
            entity: Entity to attach the component to
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            The created component instance or None if type not found
        """
        component_type = self._components.get(type_name)
        if not component_type:
            return None
        return component_type(entity, *args, **kwargs)

# Export component types
__all__ = [
    'ComponentRegistry',
    'Component',
    'TransformComponent', 
    'RenderComponent',
    'CollisionComponent',
    'InputComponent',
    'ScreenWrapComponent'
] 