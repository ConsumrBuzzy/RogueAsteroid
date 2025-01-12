"""Input component for handling entity input and key bindings."""
from typing import Dict, List, Callable, Any, Optional
import pygame
from .component import Component

class InputComponent(Component):
    """Component for managing entity input.
    
    Provides:
    - Key binding management
    - Input state tracking
    - Action mapping
    - Multiple control schemes
    - Input buffering
    """
    
    def __init__(self, entity):
        """Initialize input component.
        
        Args:
            entity: Entity this component belongs to
        """
        super().__init__(entity)
        self._key_bindings: Dict[str, List[int]] = {}  # Action -> List of key codes
        self._active_keys: Dict[int, bool] = {}  # Key code -> Is pressed
        self._action_handlers: Dict[str, Callable] = {}  # Action -> Handler function
        self._buffer_time = 0.1  # Input buffer window in seconds
        self._buffered_actions: Dict[str, float] = {}  # Action -> Buffer time left
        
        print("InputComponent initialized")
    
    def update(self, dt: float) -> None:
        """Update input state and handle buffered actions.
        
        Args:
            dt: Delta time in seconds
        """
        if not self.enabled:
            return
            
        # Update input buffer timers
        to_remove = []
        for action, time_left in self._buffered_actions.items():
            time_left -= dt
            if time_left <= 0:
                to_remove.append(action)
            else:
                self._buffered_actions[action] = time_left
                
        # Remove expired buffered actions
        for action in to_remove:
            del self._buffered_actions[action]
    
    def bind_action(self, action: str, keys: List[int], handler: Callable) -> None:
        """Bind an action to keys and handler.
        
        Args:
            action: Name of the action
            keys: List of pygame key codes
            handler: Function to call when action is triggered
        """
        self._key_bindings[action] = keys
        self._action_handlers[action] = handler
        print(f"Bound action '{action}' to keys {keys}")
    
    def unbind_action(self, action: str) -> None:
        """Unbind an action.
        
        Args:
            action: Name of the action to unbind
        """
        if action in self._key_bindings:
            del self._key_bindings[action]
        if action in self._action_handlers:
            del self._action_handlers[action]
        print(f"Unbound action '{action}'")
    
    def clear_bindings(self) -> None:
        """Clear all key bindings."""
        self._key_bindings.clear()
        self._action_handlers.clear()
        self._active_keys.clear()
        print("Cleared all key bindings")
    
    def handle_keydown(self, key: int) -> None:
        """Handle key press event.
        
        Args:
            key: Pygame key code that was pressed
        """
        if not self.enabled:
            return
            
        self._active_keys[key] = True
        
        # Check for actions triggered by this key
        for action, keys in self._key_bindings.items():
            if key in keys and action in self._action_handlers:
                handler = self._action_handlers[action]
                handler()
                # Buffer the action
                self._buffered_actions[action] = self._buffer_time
    
    def handle_keyup(self, key: int) -> None:
        """Handle key release event.
        
        Args:
            key: Pygame key code that was released
        """
        if not self.enabled:
            return
            
        self._active_keys[key] = False
    
    def is_action_pressed(self, action: str) -> bool:
        """Check if any key for an action is currently pressed.
        
        Args:
            action: Name of the action to check
            
        Returns:
            True if any key for the action is pressed
        """
        if action not in self._key_bindings:
            return False
            
        return any(self._active_keys.get(key, False) 
                  for key in self._key_bindings[action])
    
    def is_action_buffered(self, action: str) -> bool:
        """Check if an action is currently in the input buffer.
        
        Args:
            action: Name of the action to check
            
        Returns:
            True if the action is buffered
        """
        return action in self._buffered_actions
    
    def set_buffer_time(self, time: float) -> None:
        """Set the input buffer window time.
        
        Args:
            time: Buffer window in seconds
        """
        self._buffer_time = max(0, time)
        print(f"Set input buffer time to {time} seconds")
    
    def get_active_actions(self) -> List[str]:
        """Get list of currently active actions.
        
        Returns:
            List of action names that are currently pressed
        """
        return [action for action in self._key_bindings.keys()
                if self.is_action_pressed(action)] 