"""Input component for handling entity input."""
import math
import pygame
from typing import Dict, List, Set, Callable, Any, Tuple
from .base import Component
from .transform import TransformComponent
from .physics import PhysicsComponent
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
        """Handle key press events."""
        # Add key to pressed keys set
        self.pressed_keys.add(key)
        
        if self.control_scheme == 'arrows':
            if key == pygame.K_UP:
                self._handle_forward_thrust()
            elif key == pygame.K_DOWN:
                self._handle_reverse_thrust()
            elif key == pygame.K_LEFT:
                self._handle_rotate_left()
            elif key == pygame.K_RIGHT:
                self._handle_rotate_right()
            elif key == pygame.K_SPACE:
                self.entity.fire_bullet()
        else:  # WASD controls
            if key == pygame.K_w:
                self._handle_forward_thrust()
            elif key == pygame.K_s:
                self._handle_reverse_thrust()
            elif key == pygame.K_a:
                self._handle_rotate_left()
            elif key == pygame.K_d:
                self._handle_rotate_right()
            elif key == pygame.K_SPACE:
                self.entity.fire_bullet()
                
    def _handle_forward_thrust(self):
        """Apply forward thrust and create particle effects."""
        physics = self.entity.get_component(PhysicsComponent)
        transform = self.entity.get_component(TransformComponent)
        if physics and transform:
            # Calculate thrust direction based on ship rotation
            angle_rad = math.radians(transform.rotation)
            thrust_dir = pygame.Vector2(
                math.cos(angle_rad),
                math.sin(angle_rad)
            )
            physics.apply_force(thrust_dir * SHIP_ACCELERATION)
            
            # Create thrust particles at back of ship
            offset = -thrust_dir * 20  # 20 pixels behind ship
            left_offset = pygame.Vector2(-thrust_dir.y, thrust_dir.x) * 5
            right_offset = pygame.Vector2(thrust_dir.y, -thrust_dir.x) * 5
            
            # Create particles at both back corners
            self.entity.game.particle_system.emit_thrust_particles(
                transform.position + offset + left_offset,
                -thrust_dir
            )
            self.entity.game.particle_system.emit_thrust_particles(
                transform.position + offset + right_offset,
                -thrust_dir
            )
            
    def _handle_reverse_thrust(self):
        """Apply reverse thrust and create particle effects."""
        physics = self.entity.get_component(PhysicsComponent)
        transform = self.entity.get_component(TransformComponent)
        if physics and transform:
            # Calculate thrust direction based on ship rotation
            angle_rad = math.radians(transform.rotation)
            thrust_dir = pygame.Vector2(
                math.cos(angle_rad),
                math.sin(angle_rad)
            )
            physics.apply_force(-thrust_dir * SHIP_ACCELERATION * 0.7)  # Reverse thrust is 70% as powerful
            
            # Create thrust particles at front of ship
            offset = thrust_dir * 15  # 15 pixels in front of ship
            self.entity.game.particle_system.emit_thrust_particles(
                transform.position + offset,
                thrust_dir
            )
            
    def _handle_rotate_left(self):
        """Rotate ship left and create side thrust particles."""
        transform = self.entity.get_component(TransformComponent)
        if transform:
            # Calculate rotation change
            dt = self.entity.game.game_loop.dt
            rotation_change = SHIP_ROTATION_SPEED * dt
            transform.rotation -= rotation_change
            print(f"Rotating left: change={rotation_change:.2f}, new rotation={transform.rotation:.2f}")
            
            # Create thrust particles on right side
            angle_rad = math.radians(transform.rotation)
            ship_dir = pygame.Vector2(
                math.sin(angle_rad),
                -math.cos(angle_rad)
            )
            right_offset = pygame.Vector2(-ship_dir.y, ship_dir.x) * 15  # Perpendicular to ship direction
            
            # Emit circular particles for thrust effect
            self.entity.game.particle_system.emit_circular(
                position=transform.position + right_offset,
                color=(255, 200, 50),  # Orange-yellow color
                count=3,  # Small number of particles per frame
                lifetime=(0.1, 0.3),  # Short-lived particles
                speed_range=(50, 100),  # Moderate speed
                size_range=(1, 2)  # Small particles
            )
            
    def _handle_rotate_right(self):
        """Rotate ship right and create side thrust particles."""
        transform = self.entity.get_component(TransformComponent)
        if transform:
            # Calculate rotation change
            dt = self.entity.game.game_loop.dt
            rotation_change = SHIP_ROTATION_SPEED * dt
            transform.rotation += rotation_change
            print(f"Rotating right: change={rotation_change:.2f}, new rotation={transform.rotation:.2f}")
            
            # Create thrust particles on left side
            angle_rad = math.radians(transform.rotation)
            ship_dir = pygame.Vector2(
                math.sin(angle_rad),
                -math.cos(angle_rad)
            )
            left_offset = pygame.Vector2(ship_dir.y, -ship_dir.x) * 15  # Perpendicular to ship direction
            
            # Emit circular particles for thrust effect
            self.entity.game.particle_system.emit_circular(
                position=transform.position + left_offset,
                color=(255, 200, 50),  # Orange-yellow color
                count=3,  # Small number of particles per frame
                lifetime=(0.1, 0.3),  # Short-lived particles
                speed_range=(50, 100),  # Moderate speed
                size_range=(1, 2)  # Small particles
            )
    
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
        # Handle continuous rotation
        if self.control_scheme == 'arrows':
            if pygame.K_LEFT in self.pressed_keys:
                self._handle_rotate_left()
            if pygame.K_RIGHT in self.pressed_keys:
                self._handle_rotate_right()
        else:  # WASD controls
            if pygame.K_a in self.pressed_keys:
                self._handle_rotate_left()
            if pygame.K_d in self.pressed_keys:
                self._handle_rotate_right()
                
        # Handle other continuous actions from key bindings
        for key in self.pressed_keys:
            if key in self.key_bindings:
                for action, _, continuous in self.key_bindings[key]:
                    if continuous:
                        action() 