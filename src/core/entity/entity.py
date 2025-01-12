"""Base entity class for game objects."""
from typing import Dict, Type, Optional, Any
from uuid import uuid4
from ..components import Component, ComponentRegistry

class Entity:
    """Base class for all game entities.
    
    Provides:
    - Component management
    - Lifecycle hooks
    - Unique identification
    - Update/draw pipeline
    - Debug support
    """
    
    def __init__(self, game, x: float = 0, y: float = 0):
        """Initialize entity.
        
        Args:
            game: Game instance this entity belongs to
            x: Initial x position
            y: Initial y position
        """
        self.game = game
        self.id = str(uuid4())
        self._components: Dict[str, Component] = {}
        self._is_destroyed = False
        self._registry = ComponentRegistry()
        
        print(f"Entity {self.id} initialized at ({x}, {y})")
    
    def add_component(self, component_type: str, **kwargs) -> Optional[Component]:
        """Add a component to the entity.
        
        Args:
            component_type: Type name of component to add
            **kwargs: Additional arguments for component initialization
            
        Returns:
            Added component instance or None if creation failed
            
        Raises:
            ValueError: If component type already exists on entity
        """
        if component_type in self._components:
            raise ValueError(f"Entity already has component of type {component_type}")
            
        component = self._registry.create_component(component_type, self, **kwargs)
        if component:
            self._components[component_type] = component
            print(f"Added {component_type} to entity {self.id}")
        return component
    
    def get_component(self, component_type: str) -> Optional[Component]:
        """Get a component by type.
        
        Args:
            component_type: Type name of component to get
            
        Returns:
            Component instance or None if not found
        """
        return self._components.get(component_type)
    
    def has_component(self, component_type: str) -> bool:
        """Check if entity has a component type.
        
        Args:
            component_type: Type name to check for
            
        Returns:
            True if entity has component type
        """
        return component_type in self._components
    
    def remove_component(self, component_type: str) -> None:
        """Remove a component from the entity.
        
        Args:
            component_type: Type name of component to remove
        """
        if component_type in self._components:
            component = self._components[component_type]
            component.enabled = False
            del self._components[component_type]
            print(f"Removed {component_type} from entity {self.id}")
    
    def update(self, dt: float) -> None:
        """Update entity and all its components.
        
        Args:
            dt: Delta time in seconds
        """
        if self._is_destroyed:
            return
            
        for component in self._components.values():
            if component.enabled:
                component.update(dt)
    
    def draw(self, screen) -> None:
        """Draw entity using its render component.
        
        Args:
            screen: Pygame surface to draw on
        """
        if self._is_destroyed:
            return
            
        render = self.get_component('RenderComponent')
        if render and render.enabled:
            render.draw(screen)
    
    def destroy(self) -> None:
        """Destroy the entity and clean up its components."""
        if self._is_destroyed:
            return
            
        self._is_destroyed = True
        for component in self._components.values():
            component.enabled = False
        self._components.clear()
        print(f"Entity {self.id} destroyed")
    
    @property
    def is_destroyed(self) -> bool:
        """Check if entity is destroyed."""
        return self._is_destroyed
    
    def __str__(self) -> str:
        """Get string representation of entity."""
        return f"Entity({self.id})" 