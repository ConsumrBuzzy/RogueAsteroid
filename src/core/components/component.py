"""Base component class for entity components."""
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..entity.entity import Entity

class Component:
    """Base class for all entity components."""
    
    def __init__(self, entity: 'Entity', **kwargs):
        """Initialize the component.
        
        Args:
            entity: The entity this component belongs to.
            **kwargs: Additional initialization parameters.
        """
        self.entity = entity
        self.active = True
        self._initialized = False
        
    def initialize(self) -> None:
        """Initialize the component."""
        if self._initialized:
            return
        self._initialized = True
        
    def update(self, dt: float) -> None:
        """Update the component.
        
        Args:
            dt: Time elapsed since last update in seconds.
        """
        pass
        
    def destroy(self) -> None:
        """Clean up and destroy the component."""
        self.active = False
        self._initialized = False
        
    def get_component(self, component_type: type) -> Any:
        """Get another component from the parent entity.
        
        Args:
            component_type: The type of component to get.
            
        Returns:
            The component instance if found, None otherwise.
        """
        return self.entity.get_component(component_type) 