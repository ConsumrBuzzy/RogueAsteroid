"""Base entity class for game objects."""
from typing import Dict, Type, Optional, TypeVar, Any
import pygame

T = TypeVar('T')

class Entity:
    """Base class for all game entities."""
    
    def __init__(self, game):
        """Initialize the entity.
        
        Args:
            game: The game instance this entity belongs to.
        """
        self.game = game
        self._components: Dict[Type, Any] = {}
        self._initialized = False
        self.active = True
        
    def add_component(self, component_type: Type[T], **kwargs) -> T:
        """Add a component to the entity.
        
        Args:
            component_type: The type of component to add.
            **kwargs: Additional arguments to pass to the component constructor.
            
        Returns:
            The created component instance.
            
        Raises:
            ValueError: If component type is invalid or already exists.
        """
        if not component_type:
            raise ValueError("Component type cannot be None")
            
        if component_type in self._components:
            raise ValueError(f"Component {component_type.__name__} already exists")
            
        component = component_type(self, **kwargs)
        self._components[component_type] = component
        return component
        
    def get_component(self, component_type: Type[T]) -> Optional[T]:
        """Get a component by type.
        
        Args:
            component_type: The type of component to get.
            
        Returns:
            The component instance if found, None otherwise.
        """
        return self._components.get(component_type)
        
    def has_component(self, component_type: Type) -> bool:
        """Check if entity has a component.
        
        Args:
            component_type: The type of component to check for.
            
        Returns:
            True if the component exists, False otherwise.
        """
        return component_type in self._components
        
    def remove_component(self, component_type: Type) -> None:
        """Remove a component from the entity.
        
        Args:
            component_type: The type of component to remove.
        """
        if component_type in self._components:
            component = self._components[component_type]
            if hasattr(component, 'cleanup'):
                component.cleanup()
            del self._components[component_type]
            
    def initialize(self) -> None:
        """Initialize the entity and its components."""
        if self._initialized:
            return
            
        # Initialize all components
        for component in self._components.values():
            if hasattr(component, 'initialize'):
                component.initialize()
                
        self._initialized = True
        
    def update(self, dt: float) -> None:
        """Update the entity and its components.
        
        Args:
            dt: Time elapsed since last update in seconds.
        """
        if not self.active or not self._initialized:
            return
            
        # Update all components
        for component in self._components.values():
            if hasattr(component, 'update'):
                component.update(dt)
                
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the entity and its components.
        
        Args:
            surface: The surface to draw on.
        """
        if not self.active or not self._initialized:
            return
            
        # Draw all components
        for component in self._components.values():
            if hasattr(component, 'draw'):
                component.draw(surface)
                
    def cleanup(self) -> None:
        """Clean up the entity and its components."""
        # Clean up all components
        for component in list(self._components.values()):
            if hasattr(component, 'cleanup'):
                component.cleanup()
        self._components.clear()
        self.active = False
        self._initialized = False 