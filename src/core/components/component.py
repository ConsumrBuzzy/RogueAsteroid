"""Base component class for game objects."""
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..entity.entity import Entity

class Component:
    """Base class for all game components.
    
    Provides:
    - Entity attachment
    - Lifecycle hooks
    - Component enable/disable
    - Debug support
    """
    
    def __init__(self, entity: 'Entity'):
        """Initialize the component.
        
        Args:
            entity: Entity this component belongs to
        """
        self._entity = entity
        self._enabled = True
        self._initialized = False
        
    @property
    def entity(self) -> 'Entity':
        """Get the entity this component belongs to.
        
        Returns:
            Parent entity
        """
        return self._entity
        
    @property
    def enabled(self) -> bool:
        """Check if component is enabled.
        
        Returns:
            True if component is enabled
        """
        return self._enabled
        
    def enable(self) -> None:
        """Enable the component."""
        if not self._enabled:
            self._enabled = True
            self.on_enable()
            
    def disable(self) -> None:
        """Disable the component."""
        if self._enabled:
            self._enabled = False
            self.on_disable()
            
    def initialize(self) -> None:
        """Initialize the component.
        
        Called when component is first added to an entity.
        """
        if not self._initialized:
            self.on_initialize()
            self._initialized = True
            
    def destroy(self) -> None:
        """Destroy the component.
        
        Called when component is removed from an entity.
        """
        self.on_destroy()
        self._enabled = False
        self._initialized = False
        
    def update(self, dt: float) -> None:
        """Update the component.
        
        Args:
            dt: Delta time in seconds
        """
        if self._enabled:
            self.on_update(dt)
            
    def on_initialize(self) -> None:
        """Called when component is initialized."""
        pass
        
    def on_destroy(self) -> None:
        """Called when component is destroyed."""
        pass
        
    def on_enable(self) -> None:
        """Called when component is enabled."""
        pass
        
    def on_disable(self) -> None:
        """Called when component is disabled."""
        pass
        
    def on_update(self, dt: float) -> None:
        """Called when component is updated.
        
        Args:
            dt: Delta time in seconds
        """
        pass 