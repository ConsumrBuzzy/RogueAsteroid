"""Input service for handling game input."""
from typing import Dict, Set, Callable, List
import pygame
from enum import Enum, auto

class InputAction(Enum):
    """Input actions enumeration."""
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    SHOOT = auto()
    PAUSE = auto()
    MENU_UP = auto()
    MENU_DOWN = auto()
    MENU_SELECT = auto()
    MENU_BACK = auto()

class InputService:
    """Service for handling game input.
    
    Provides:
    - Action-based input mapping
    - Multiple control schemes
    - Input state tracking
    - Event handling
    """
    
    def __init__(self):
        """Initialize the input service."""
        self._key_map: Dict[int, InputAction] = {}
        self._pressed_keys: Set[int] = set()
        self._action_handlers: Dict[InputAction, List[Callable]] = {}
        
        # Initialize handlers for each action
        for action in InputAction:
            self._action_handlers[action] = []
            
        # Set up default key bindings
        self._setup_default_bindings()
        print("InputService initialized")
        
    def _setup_default_bindings(self) -> None:
        """Set up default key bindings."""
        # Arrow key controls (in-game)
        self._key_map[pygame.K_UP] = InputAction.MOVE_UP
        self._key_map[pygame.K_DOWN] = InputAction.MOVE_DOWN
        self._key_map[pygame.K_LEFT] = InputAction.MOVE_LEFT
        self._key_map[pygame.K_RIGHT] = InputAction.MOVE_RIGHT
        
        # WASD controls (in-game)
        self._key_map[pygame.K_w] = InputAction.MOVE_UP
        self._key_map[pygame.K_s] = InputAction.MOVE_DOWN
        self._key_map[pygame.K_a] = InputAction.MOVE_LEFT
        self._key_map[pygame.K_d] = InputAction.MOVE_RIGHT
        
        # Action keys
        self._key_map[pygame.K_SPACE] = InputAction.SHOOT
        self._key_map[pygame.K_RETURN] = InputAction.SHOOT
        self._key_map[pygame.K_ESCAPE] = InputAction.PAUSE
        
        # Menu controls (separate from movement)
        self._key_map[pygame.K_KP8] = InputAction.MENU_UP  # Numpad 8
        self._key_map[pygame.K_KP2] = InputAction.MENU_DOWN  # Numpad 2
        self._key_map[pygame.K_KP_ENTER] = InputAction.MENU_SELECT  # Numpad Enter
        self._key_map[pygame.K_BACKSPACE] = InputAction.MENU_BACK  # Backspace
        
    def add_handler(self, action: InputAction, handler: Callable) -> None:
        """Add a handler for an input action.
        
        Args:
            action: Input action to handle
            handler: Function to call when action occurs
        """
        if action in self._action_handlers:
            self._action_handlers[action].append(handler)
            
    def remove_handler(self, action: InputAction, handler: Callable) -> None:
        """Remove a handler for an input action.
        
        Args:
            action: Input action to remove handler from
            handler: Handler to remove
        """
        if action in self._action_handlers and handler in self._action_handlers[action]:
            self._action_handlers[action].remove(handler)
            
    def is_action_pressed(self, action: InputAction) -> bool:
        """Check if an action is currently pressed.
        
        Args:
            action: Input action to check
            
        Returns:
            True if any key for the action is pressed
        """
        return any(key in self._pressed_keys for key, act in self._key_map.items() if act == action)
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a pygame input event.
        
        Args:
            event: Pygame event to handle
        """
        if event.type == pygame.KEYDOWN:
            self._pressed_keys.add(event.key)
            if action := self._key_map.get(event.key):
                for handler in self._action_handlers[action]:
                    handler()
                    
        elif event.type == pygame.KEYUP:
            self._pressed_keys.discard(event.key)
            
    def update(self) -> None:
        """Update input state."""
        # Handle continuous input for pressed keys
        for key in self._pressed_keys:
            if action := self._key_map.get(key):
                for handler in self._action_handlers[action]:
                    handler()
                    
    def cleanup(self) -> None:
        """Clean up the service."""
        self._pressed_keys.clear()
        self._action_handlers.clear()
        print("InputService cleaned up") 