"""Base component class for the entity component system."""
from typing import Optional, Any
from uuid import uuid4

class Component:
    """Base class for all entity components.
    
    Provides:
    - Entity attachment
    - Lifecycle hooks
    - Unique identification
    - Debug support
    """
    
    def __init__(self, entity: Any):
        """Initialize component.
        
        Args:
            entity: Entity this component belongs to
        """
        self.entity = entity
        self.id = str(uuid4())  # Unique component identifier
        self.enabled = True
        
        # Debug info
        print(f"Component {self.__class__.__name__} ({self.id}) initialized")
    
    def update(self, dt: float) -> None:
        """Update component logic.
        
        Args:
            dt: Delta time in seconds
        """
        if not self.enabled:
            return
    
    def cleanup(self) -> None:
        """Clean up component resources."""
        self.enabled = False
        self.entity = None
        print(f"Component {self.__class__.__name__} ({self.id}) cleaned up")
    
    def enable(self) -> None:
        """Enable the component."""
        self.enabled = True
        print(f"Component {self.__class__.__name__} ({self.id}) enabled")
    
    def disable(self) -> None:
        """Disable the component."""
        self.enabled = False
        print(f"Component {self.__class__.__name__} ({self.id}) disabled")
    
    def get_sibling_component(self, component_type: type) -> Optional[Any]:
        """Get another component from the same entity.
        
        Args:
            component_type: Type of component to get
            
        Returns:
            Component instance if found, None otherwise
        """
        return self.entity.get_component(component_type) if self.entity else None
    
    def __str__(self) -> str:
        """String representation of component."""
        return f"{self.__class__.__name__}(id={self.id}, enabled={self.enabled})" 