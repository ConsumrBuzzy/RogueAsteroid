"""Base component module."""
from typing import Any, TypeVar, Type

T = TypeVar('T', bound='Component')

class Component:
    """Base class for all components."""
    def __init__(self, entity):
        self.entity = entity
        self.enabled = True
    
    def update(self, dt: float) -> None:
        """Update component state.
        
        Args:
            dt: Time delta in seconds.
        """
        pass
    
    def start(self) -> None:
        """Called when component is first added to an entity."""
        pass
    
    def destroy(self) -> None:
        """Called when component is removed from an entity."""
        pass
    
    def enable(self) -> None:
        """Enable the component."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable the component."""
        self.enabled = False 