"""Input handling service for game-wide input management."""
from typing import Dict, List, Set, Callable, Any, Optional
import pygame
from enum import Enum, auto

class InputAction(Enum):
    """Enumeration of all possible input actions."""
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    SHOOT = auto()
    PAUSE = auto()
    CONFIRM = auto()
    CANCEL = auto()
    MENU = auto()

class InputService:
    """Service for game-wide input handling.
    
    Provides:
    - Action mapping
    - Input state tracking
    - Multiple control schemes
    - Event filtering
    - Input buffering
    - Debug support
    """
    
    def __init__(self):
        """Initialize the input service."""
        self._action_bindings: Dict[InputAction, List[int]] = {}
        self._pressed_keys: Set[int] = set()
        self._action_handlers: Dict[InputAction, List[Callable]] = {}
        self._control_scheme: str = 'arrows'  # 'arrows' or 'wasd'
        print("InputService initialized")
        
    def bind_action(self, action: InputAction, keys: List[int]) -> None:
        """Bind keys to an action.
        
        Args:
            action: Action to bind keys to
            keys: List of pygame key constants
        """
        self._action_bindings[action] = keys
        print(f"Bound keys to action: {action.name}")
        
    def register_handler(self, action: InputAction, handler: Callable) -> None:
        """Register a handler for an action.
        
        Args:
            action: Action to handle
            handler: Callback function for when action occurs
        """
        if action not in self._action_handlers:
            self._action_handlers[action] = []
        self._action_handlers[action].append(handler)
        print(f"Registered handler for action: {action.name}")
        
    def remove_handler(self, action: InputAction, handler: Callable) -> None:
        """Remove a handler for an action.
        
        Args:
            action: Action to remove handler from
            handler: Handler to remove
        """
        if action in self._action_handlers and handler in self._action_handlers[action]:
            self._action_handlers[action].remove(handler)
            print(f"Removed handler for action: {action.name}")
            
    def set_control_scheme(self, scheme: str) -> None:
        """Set the current control scheme.
        
        Args:
            scheme: Control scheme to use ('arrows' or 'wasd')
        """
        if scheme not in ['arrows', 'wasd']:
            print(f"Invalid control scheme: {scheme}")
            return
            
        self._control_scheme = scheme
        self._update_bindings()
        print(f"Control scheme set to: {scheme}")
        
    def _update_bindings(self) -> None:
        """Update key bindings based on current control scheme."""
        if self._control_scheme == 'arrows':
            movement_keys = {
                InputAction.MOVE_UP: [pygame.K_UP, pygame.K_KP8],
                InputAction.MOVE_DOWN: [pygame.K_DOWN, pygame.K_KP5],
                InputAction.MOVE_LEFT: [pygame.K_LEFT, pygame.K_KP4],
                InputAction.MOVE_RIGHT: [pygame.K_RIGHT, pygame.K_KP6]
            }
        else:  # wasd
            movement_keys = {
                InputAction.MOVE_UP: [pygame.K_w],
                InputAction.MOVE_DOWN: [pygame.K_s],
                InputAction.MOVE_LEFT: [pygame.K_a],
                InputAction.MOVE_RIGHT: [pygame.K_d]
            }
            
        # Common bindings
        common_keys = {
            InputAction.SHOOT: [pygame.K_SPACE, pygame.K_KP_ENTER],
            InputAction.PAUSE: [pygame.K_ESCAPE, pygame.K_p],
            InputAction.CONFIRM: [pygame.K_RETURN, pygame.K_KP_ENTER],
            InputAction.CANCEL: [pygame.K_ESCAPE],
            InputAction.MENU: [pygame.K_ESCAPE]
        }
        
        # Update all bindings
        self._action_bindings.clear()
        self._action_bindings.update(movement_keys)
        self._action_bindings.update(common_keys)
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a pygame event.
        
        Args:
            event: Pygame event to handle
        """
        if event.type == pygame.KEYDOWN:
            self._pressed_keys.add(event.key)
            self._check_actions(event.key, True)
        elif event.type == pygame.KEYUP:
            self._pressed_keys.discard(event.key)
            self._check_actions(event.key, False)
            
    def _check_actions(self, key: int, is_pressed: bool) -> None:
        """Check if any actions should trigger from a key event.
        
        Args:
            key: Key that changed state
            is_pressed: Whether key was pressed or released
        """
        for action, keys in self._action_bindings.items():
            if key in keys:
                if is_pressed and action in self._action_handlers:
                    for handler in self._action_handlers[action]:
                        try:
                            handler()
                        except Exception as e:
                            print(f"Error in input handler for {action.name}: {e}")
                            
    def is_action_pressed(self, action: InputAction) -> bool:
        """Check if any key for an action is currently pressed.
        
        Args:
            action: Action to check
            
        Returns:
            True if any key for the action is pressed
        """
        if action not in self._action_bindings:
            return False
        return any(key in self._pressed_keys for key in self._action_bindings[action])
        
    def clear(self) -> None:
        """Clear all input state and handlers."""
        self._pressed_keys.clear()
        self._action_handlers.clear()
        print("Input service cleared") 