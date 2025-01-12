"""Input component for entity control."""
from typing import Dict, List, Callable, Optional
import pygame
from src.core.entities.base import Component, Entity

class InputComponent(Component):
    """Component for handling entity input."""
    
    def __init__(self, entity: Entity):
        """Initialize the input component.
        
        Args:
            entity: The entity this component belongs to
        """
        super().__init__(entity)
        self._action_bindings: Dict[str, List[int]] = {}  # Action name -> key list
        self._action_handlers: Dict[str, Callable[[], None]] = {}  # Action name -> handler
    
    def bind_action(self, action: str, keys: List[int], handler: Callable[[], None]) -> None:
        """Bind an action to keys and handler.
        
        Args:
            action: Name of the action
            keys: List of pygame key constants
            handler: Function to call when action is triggered
        """
        self._action_bindings[action] = keys
        self._action_handlers[action] = handler
    
    def clear_bindings(self) -> None:
        """Clear all action bindings."""
        self._action_bindings.clear()
        self._action_handlers.clear()
    
    def update(self, dt: float) -> None:
        """Check for input and trigger actions.
        
        Args:
            dt: Time delta in seconds
        """
        if not self.active:
            return
            
        # Get pressed keys
        keys = pygame.key.get_pressed()
        
        # Check each action
        for action, bound_keys in self._action_bindings.items():
            # If any bound key is pressed
            if any(keys[key] for key in bound_keys):
                handler = self._action_handlers.get(action)
                if handler:
                    handler()
    
    def get_handler(self, action: str) -> Optional[Callable[[], None]]:
        """Get the handler for an action.
        
        Args:
            action: Name of the action
            
        Returns:
            The handler function if bound, None otherwise
        """
        return self._action_handlers.get(action)
    
    def is_action_bound(self, action: str) -> bool:
        """Check if an action is bound.
        
        Args:
            action: Name of the action
            
        Returns:
            True if the action is bound to keys and has a handler
        """
        return action in self._action_bindings and action in self._action_handlers 