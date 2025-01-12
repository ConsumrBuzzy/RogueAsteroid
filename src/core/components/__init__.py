"""Component system for RogueAsteroid."""
from typing import Dict, Type, Any, Optional

from .base import (
    Component,
    TransformComponent,
    RenderComponent,
    CollisionComponent,
    InputComponent,
    ScreenWrapComponent
)
from .physics import PhysicsComponent
from .effect import EffectComponent
from .wave import WaveComponent
from .ui import UIComponent
from .timer import TimerComponent
from .score import ScoreComponent
from .health import HealthComponent
from .debug import DebugComponent
from .audio import AudioComponent

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
        self.register_component('PhysicsComponent', PhysicsComponent)
        self.register_component('EffectComponent', EffectComponent)
        self.register_component('WaveComponent', WaveComponent)
        self.register_component('UIComponent', UIComponent)
        self.register_component('TimerComponent', TimerComponent)
        self.register_component('ScoreComponent', ScoreComponent)
        self.register_component('HealthComponent', HealthComponent)
        self.register_component('DebugComponent', DebugComponent)
        self.register_component('AudioComponent', AudioComponent)
    
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

__all__ = [
    'Component',
    'ComponentRegistry',
    'TransformComponent',
    'RenderComponent',
    'CollisionComponent',
    'InputComponent',
    'ScreenWrapComponent',
    'PhysicsComponent',
    'EffectComponent',
    'WaveComponent',
    'UIComponent',
    'TimerComponent',
    'ScoreComponent',
    'HealthComponent',
    'DebugComponent',
    'AudioComponent'
]