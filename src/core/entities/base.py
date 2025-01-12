"""Base classes for entity component system.

This module provides the foundational classes for the entity component system (ECS).
The system is designed to be flexible, extensible, and maintainable, following SOLID principles.
"""

from typing import Dict, Type, TypeVar, Optional, List, Tuple, Any, Union

T = TypeVar('T', bound='Component')

class Entity:
    """Base class for all game entities.
    
    An entity is a container for components that define its behavior and properties.
    Each entity has a unique set of components that can be added, retrieved, and updated.
    """
    
    def __init__(self, game: Any) -> None:
        """Initialize the entity with a reference to the game instance.
        
        Args:
            game: The game instance this entity belongs to.
        """
        self._game = game
        self._components: Dict[str, 'Component'] = {}
    
    @property
    def game(self) -> Any:
        """Get the game instance this entity belongs to."""
        return self._game
    
    def add_component(self, component_type: Type[T], *args: Any, **kwargs: Any) -> T:
        """Add a component to the entity.
        
        Args:
            component_type: The type of component to add.
            *args: Positional arguments for component initialization.
            **kwargs: Keyword arguments for component initialization.
            
        Returns:
            The newly created component instance.
            
        Raises:
            ValueError: If a component of the same type already exists.
        """
        name = component_type.__name__.lower().replace('component', '')
        if name in self._components:
            raise ValueError(f"Component {name} already exists on this entity")
            
        component = component_type(self, *args, **kwargs)
        self._components[name] = component
        return component
    
    def get_component(self, component_type_or_name: Union[Type[T], str]) -> Optional[T]:
        """Get a component by type or name.
        
        Args:
            component_type_or_name: The component type class or name string.
            
        Returns:
            The component if found, None otherwise.
        """
        if isinstance(component_type_or_name, str):
            name = component_type_or_name.lower().replace('component', '')
        else:
            name = component_type_or_name.__name__.lower().replace('component', '')
        return self._components.get(name)
    
    def update(self, dt: float) -> None:
        """Update all components of the entity.
        
        Args:
            dt: Delta time since last update in seconds.
        """
        for component in self._components.values():
            component.update(dt)

class Component:
    """Base class for all components.
    
    Components define specific behaviors and properties that can be attached to entities.
    Each component should have a single responsibility following the Single Responsibility Principle.
    """
    
    def __init__(self, entity: Entity) -> None:
        """Initialize the component with a reference to its entity.
        
        Args:
            entity: The entity this component belongs to.
        """
        self._entity = entity
        self._enabled = True
    
    @property
    def entity(self) -> Entity:
        """Get the entity this component belongs to."""
        return self._entity
    
    @property
    def enabled(self) -> bool:
        """Get whether the component is enabled."""
        return self._enabled
    
    def enable(self) -> None:
        """Enable the component."""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable the component."""
        self._enabled = False
    
    def update(self, dt: float) -> None:
        """Update the component's state.
        
        Args:
            dt: Delta time since last update in seconds.
        """
        pass 