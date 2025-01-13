"""Input component for handling entity input."""
import math
import pygame
import random
from typing import Dict, List, Set, Callable, Any, Tuple
from src.core.entities.components.base import Component
from src.core.entities.components.transform import TransformComponent
from src.core.entities.components.physics import PhysicsComponent
from src.core.constants import SHIP_ACCELERATION, SHIP_ROTATION_SPEED
from src.core.logging import get_logger

class InputComponent(Component):
    """Component for handling input for an entity."""
    
    def __init__(self, entity, control_scheme: str = 'arrows'):
        """Initialize the input component.
        
        Args:
            entity: The entity this component belongs to
            control_scheme: The control scheme to use ('arrows' or 'wasd')
        """
        super().__init__(entity)
        self.logger = get_logger()
        self.control_scheme = control_scheme
        self.key_bindings: Dict[int, Tuple[Callable[[], None], bool]] = {}
        self.pressed_keys: Set[int] = set()
        self.active_keys: Set[int] = set()  # Track keys for continuous actions
        self.event_handlers: List[Callable[[pygame.event.Event], None]] = []
        self.rotation_direction = 0  # -1 for left, 1 for right, 0 for none
        self._setup_bindings()
        self.logger.debug(f"Input component initialized with {control_scheme} controls")
    
    def _setup_bindings(self) -> None:
        """Set up the key bindings based on control scheme."""
        self.key_bindings.clear()
        self.active_keys.clear()
        
        # Get the transform and physics components
        transform = self.entity.get_component(TransformComponent)
        physics = self.entity.get_component(PhysicsComponent)
        
        if not transform or not physics:
            self.logger.warning("Missing required components for input setup")
            return
            
        # Define rotation functions
        def rotate_left():
            self.rotation_direction = -1
            
        def rotate_right():
            self.rotation_direction = 1
            
        def stop_rotation():
            self.rotation_direction = 0
            
        # Define thrust function
        def apply_thrust():
            # Calculate thrust direction based on ship rotation
            angle = math.radians(transform.rotation)
            thrust_dir = pygame.Vector2(-math.sin(angle), -math.cos(angle))
            physics.apply_force(thrust_dir * SHIP_ACCELERATION)
            
        # Define shoot function
        def shoot():
            self.entity.handle_shoot()
            
        # Bind keys based on control scheme
        if self.control_scheme == 'arrows':
            self.bind_key(pygame.K_LEFT, rotate_left, True)
            self.bind_key(pygame.K_RIGHT, rotate_right, True)
            self.bind_key(pygame.K_UP, apply_thrust, True)
            self.bind_key(pygame.K_SPACE, shoot, False)
        else:  # WASD
            self.bind_key(pygame.K_a, rotate_left, True)
            self.bind_key(pygame.K_d, rotate_right, True)
            self.bind_key(pygame.K_w, apply_thrust, True)
            self.bind_key(pygame.K_SPACE, shoot, False)
        
        self.logger.debug(f"Key bindings set up for {self.control_scheme} scheme")
            
    def update_control_scheme(self, new_scheme: str) -> None:
        """Update the control scheme and rebind keys.
        
        Args:
            new_scheme: The new control scheme to use ('arrows' or 'wasd')
        """
        self.logger.info(f"Updating control scheme from {self.control_scheme} to {new_scheme}")
        self.control_scheme = new_scheme
        self._setup_bindings()
        
    def bind_key(self, key: int, action: Callable[[], None], continuous: bool = False) -> None:
        """Bind a key to an action.
        
        Args:
            key: The key to bind
            action: The action to execute
            continuous: Whether the action should be executed continuously while key is held
        """
        self.key_bindings[key] = (action, continuous)
    
    def handle_keydown(self, key: int) -> None:
        """Handle key press event."""
        if key in self.key_bindings:
            action, continuous = self.key_bindings[key]
            action()
            if continuous:
                self.active_keys.add(key)
                
    def handle_keyup(self, key: int) -> None:
        """Handle key release event."""
        if key in self.active_keys:
            self.active_keys.remove(key)
            # Stop rotation if releasing a rotation key
            if key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d]:
                self.rotation_direction = 0
                
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a pygame event."""
        if event.type == pygame.KEYDOWN:
            self.handle_keydown(event.key)
        elif event.type == pygame.KEYUP:
            self.handle_keyup(event.key)
            
    def update(self, dt: float) -> None:
        """Update continuous actions based on delta time."""
        transform = self.entity.get_component(TransformComponent)
        if transform and self.rotation_direction != 0:
            transform.rotation += SHIP_ROTATION_SPEED * self.rotation_direction * dt
            
        # Handle continuous actions for active keys
        for key in self.active_keys:
            if key in self.key_bindings:
                action, continuous = self.key_bindings[key]
                if continuous:
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