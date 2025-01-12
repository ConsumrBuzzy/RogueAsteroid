"""Input component module."""
import pygame
from typing import Dict, List, Set, Callable, Any, Tuple
from .base import Component

class InputComponent(Component):
    """Component for handling input."""
    def __init__(self, entity):
        super().__init__(entity)
        self.key_bindings: Dict[int, List[Tuple[Callable[[], None], int, bool]]] = {}
        self.key_combinations: Dict[Tuple[int, ...], Callable[[], None]] = {}
        self.pressed_keys: Set[int] = set()
        self.event_handlers: List[Callable[[pygame.event.Event], None]] = []
    
    def bind_key(self, key: int, action: Callable[[], None], priority: int = 0, continuous: bool = False) -> None:
        """Bind a key to an action with optional priority and continuous action."""
        if key not in self.key_bindings:
            self.key_bindings[key] = []
        self.key_bindings[key].append((action, priority, continuous))
        self.key_bindings[key].sort(key=lambda x: x[1], reverse=True)
    
    def bind_key_combination(self, keys: Tuple[int, ...], action: Callable[[], None]) -> None:
        """Bind a combination of keys to an action."""
        self.key_combinations[keys] = action
    
    def handle_keydown(self, key: int) -> None:
        """Handle key press."""
        self.pressed_keys.add(key)
        
        # Check key combinations
        for combo, action in self.key_combinations.items():
            if all(k in self.pressed_keys for k in combo):
                action()
        
        # Execute single key actions
        if key in self.key_bindings:
            for action, _, _ in self.key_bindings[key]:
                action()
    
    def handle_keyup(self, key: int) -> None:
        """Handle key release."""
        self.pressed_keys.discard(key)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input event."""
        if event.type == pygame.KEYDOWN:
            self.handle_keydown(event.key)
        elif event.type == pygame.KEYUP:
            self.handle_keyup(event.key)
        
        # Execute custom event handlers
        for handler in self.event_handlers:
            handler(event)
    
    def add_event_handler(self, handler: Callable[[pygame.event.Event], None]) -> None:
        """Add custom event handler."""
        self.event_handlers.append(handler)
    
    def is_key_pressed(self, key: int) -> bool:
        """Check if a key is currently pressed."""
        return key in self.pressed_keys
    
    def update(self, dt: float) -> None:
        """Handle continuous actions for held keys."""
        for key in self.pressed_keys:
            if key in self.key_bindings:
                for action, _, continuous in self.key_bindings[key]:
                    if continuous:
                        action() 