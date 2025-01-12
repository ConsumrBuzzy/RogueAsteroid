"""Component system initialization."""
from typing import Dict, Type, Any, Optional
from src.core.entities.base import (
    Component,
    TransformComponent,
    RenderComponent,
    CollisionComponent
)
from src.core.components.effect import EffectComponent
from src.core.components.physics import PhysicsComponent
from src.core.components.input import InputComponent
from src.core.components.screen_wrap import ScreenWrapComponent

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
        self.register_component('EffectComponent', EffectComponent)
        self.register_component('PhysicsComponent', PhysicsComponent)
        self.register_component('InputComponent', InputComponent)
        self.register_component('ScreenWrapComponent', ScreenWrapComponent)
        print("ComponentRegistry initialized")
    
    def register_component(self, type_name: str, component_type: Type[Component]) -> None:
        """Register a component type.
        
        Args:
            type_name: Name to register the component under
            component_type: The component class to register
        """
        self._components[type_name] = component_type
    
    def create_component(self, type_name: str, entity: Any, *args, **kwargs) -> Component:
        """Create a component instance.
        
        Args:
            type_name: Name of the component type to create
            entity: Entity to attach the component to
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            The created component instance
            
        Raises:
            KeyError: If the component type is not registered
        """
        if type_name not in self._components:
            raise KeyError(f"Unknown component type: {type_name}")
        return self._components[type_name](entity, *args, **kwargs)
    
    def get_component_type(self, type_name: str) -> Optional[Type[Component]]:
        """Get a registered component type.
        
        Args:
            type_name: Name of the component type
            
        Returns:
            The component type if registered, None otherwise
        """
        return self._components.get(type_name)

__all__ = [
    'ComponentRegistry',
    'PhysicsComponent',
    'InputComponent',
    'ScreenWrapComponent'
] 