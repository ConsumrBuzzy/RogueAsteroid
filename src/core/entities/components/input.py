"""Input component for handling entity input."""
import math
import pygame
import random
from typing import Dict, List, Set, Callable, Any, Tuple
from src.core.entities.components.base import Component
from src.core.entities.components.transform import TransformComponent
from src.core.entities.components.physics import PhysicsComponent
from src.core.constants import SHIP_ACCELERATION, SHIP_ROTATION_SPEED

class InputComponent(Component):
    """Component for handling input for an entity."""
    
    def __init__(self, entity, control_scheme: str = 'arrows'):
        """Initialize the input component.
        
        Args:
            entity: The entity this component belongs to
            control_scheme: The control scheme to use ('arrows' or 'wasd')
        """
        super().__init__(entity)
        self.control_scheme = control_scheme
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
        """Handle key press event."""
        if key in self.key_bindings:
            action, continuous = self.key_bindings[key]
            if not continuous:  # Only execute non-continuous actions on keydown
                action()
                
    def handle_keyup(self, key: int) -> None:
        """Handle key release event."""
        if key in self.key_bindings:
            action, continuous = self.key_bindings[key]
            if continuous:  # Only track continuous actions
                self.active_keys.discard(key)
                
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
        """Update continuous actions."""
        for key in self.active_keys:
            if key in self.key_bindings:
                action, continuous = self.key_bindings[key]
                if continuous:  # Only execute continuous actions during update
                    action()
    
    def _handle_turn_thrust(self, direction: str):
        """Create turn thrust particles."""
        transform = self.entity.get_component(TransformComponent)
        if transform:
            # Calculate ship direction
            angle_rad = math.radians(transform.rotation)
            ship_dir = pygame.Vector2(
                math.sin(angle_rad),
                -math.cos(angle_rad)
            )
            back_offset = -ship_dir * 20  # Bottom of ship
            
            if direction == 'left':
                # Position at left bottom corner for right turn
                left_offset = pygame.Vector2(ship_dir.y, -ship_dir.x) * 10  # Left side
                position = transform.position + back_offset + left_offset
            else:  # right turn
                # Position at right bottom corner for left turn
                right_offset = pygame.Vector2(-ship_dir.y, ship_dir.x) * 10  # Right side
                position = transform.position + back_offset + right_offset
            
            # Emit circular particles for thrust effect
            self.entity.game.particle_system.emit_circular(
                position=position,
                color=(255, 255, 0),  # Yellow color
                count=1,  # Single particle per frame
                lifetime=(0.05, 0.15),  # Very short-lived particles
                speed_range=(30, 50),  # Slower speed for smaller effect
                size_range=(1, 1)  # Tiny particles
            ) 