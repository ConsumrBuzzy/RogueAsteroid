"""Base entity class for game objects."""
from typing import Dict, Type, Optional, Any
from uuid import uuid4
import pygame

class Entity:
    """Base class for all game entities.
    
    Provides core functionality for:
    - Component management
    - Lifecycle hooks
    - Unique identification
    - Debug support
    """
    
    def __init__(self, game, x: float = 0, y: float = 0):
        """Initialize entity.
        
        Args:
            game: Reference to main game instance
            x: Initial x position
            y: Initial y position
        """
        self.game = game
        self.id = str(uuid4())  # Unique entity identifier
        self.x = x
        self.y = y
        self.components: Dict[Type, Any] = {}
        self.is_active = True
        self.is_destroyed = False
        
        # Debug info
        print(f"Entity {self.id} initialized at ({x}, {y})")
    
    def add_component(self, component_type: Type, component: Any) -> None:
        """Add a component to the entity.
        
        Args:
            component_type: Type of the component
            component: Component instance
        """
        if component_type in self.components:
            print(f"Warning: Overwriting existing {component_type.__name__} component")
        self.components[component_type] = component
        print(f"Added {component_type.__name__} to entity {self.id}")
    
    def get_component(self, component_type: Type) -> Optional[Any]:
        """Get a component by type.
        
        Args:
            component_type: Type of component to get
            
        Returns:
            Component instance if found, None otherwise
        """
        return self.components.get(component_type)
    
    def has_component(self, component_type: Type) -> bool:
        """Check if entity has a component.
        
        Args:
            component_type: Type of component to check
            
        Returns:
            True if component exists, False otherwise
        """
        return component_type in self.components
    
    def remove_component(self, component_type: Type) -> None:
        """Remove a component from the entity.
        
        Args:
            component_type: Type of component to remove
        """
        if component_type in self.components:
            del self.components[component_type]
            print(f"Removed {component_type.__name__} from entity {self.id}")
    
    def update(self, dt: float) -> None:
        """Update entity and all components.
        
        Args:
            dt: Delta time in seconds
        """
        if not self.is_active or self.is_destroyed:
            return
            
        for component in self.components.values():
            if hasattr(component, 'update'):
                component.update(dt)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw entity using its render component.
        
        Args:
            screen: Pygame surface to draw on
        """
        if not self.is_active or self.is_destroyed:
            return
            
        render_component = self.get_component('RenderComponent')
        if render_component and hasattr(render_component, 'draw'):
            render_component.draw(screen)
    
    def destroy(self) -> None:
        """Mark entity for destruction and cleanup."""
        if self.is_destroyed:
            return
            
        self.is_destroyed = True
        self.is_active = False
        
        # Cleanup components
        for component in self.components.values():
            if hasattr(component, 'cleanup'):
                component.cleanup()
        
        self.components.clear()
        print(f"Entity {self.id} destroyed")
    
    def __str__(self) -> str:
        """String representation of entity."""
        return f"Entity(id={self.id}, x={self.x}, y={self.y}, components={len(self.components)})" 