"""Core game components module."""
import pygame
from typing import Optional, Callable, List, Set, Dict, Any

class Component:
    """Base class for all components."""
    def __init__(self, entity):
        self.entity = entity
        self.enabled = True
    
    def update(self, dt: float) -> None:
        """Update component state."""
        pass

class TransformComponent(Component):
    """Component for position, rotation, and scale."""
    def __init__(self, entity):
        super().__init__(entity)
        self.position = pygame.Vector2(0, 0)
        self.rotation = 0.0
        self.scale = pygame.Vector2(1, 1)
        self.velocity = pygame.Vector2(0, 0)

class PhysicsComponent(Component):
    """Component for physics simulation."""
    def __init__(self, entity, mass: float = 1.0, max_speed: float = 100.0):
        super().__init__(entity)
        self.mass = mass
        self.max_speed = max_speed
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)
        self.angular_velocity = 0.0
        self.friction = 0.0
        self.gravity = pygame.Vector2(0, 0)
    
    def apply_force(self, force: pygame.Vector2) -> None:
        """Apply a force to the entity."""
        self.acceleration += force / self.mass
    
    def apply_impulse(self, impulse: pygame.Vector2) -> None:
        """Apply an instantaneous force."""
        self.velocity += impulse / self.mass
    
    def update(self, dt: float) -> None:
        """Update physics state."""
        # Update velocity
        self.velocity += self.acceleration * dt
        self.velocity += self.gravity * dt
        
        # Apply friction
        if self.friction > 0:
            self.velocity *= (1 - self.friction)
        
        # Enforce speed limit
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)
        
        # Update transform
        transform = self.entity.get_component(TransformComponent)
        if transform:
            transform.position += self.velocity * dt
            transform.rotation += self.angular_velocity * dt
        
        # Reset acceleration
        self.acceleration = pygame.Vector2(0, 0)

class CollisionComponent(Component):
    """Component for collision detection."""
    def __init__(self, entity):
        super().__init__(entity)
        self.radius = 10.0
        self.tag = "default"
        self.layer = 0
        self.group = 0
        self.is_static = False
        self.on_collision: Optional[Callable[[Any], None]] = None
    
    def is_colliding_with(self, other: 'CollisionComponent') -> bool:
        """Check if colliding with another entity."""
        if not self.enabled or not other.enabled:
            return False
        
        transform = self.entity.get_component(TransformComponent)
        other_transform = other.entity.get_component(TransformComponent)
        
        if not transform or not other_transform:
            return False
        
        distance = (transform.position - other_transform.position).length()
        return distance < (self.radius + other.radius)

class InputComponent(Component):
    """Component for handling input."""
    def __init__(self, entity):
        super().__init__(entity)
        self.key_bindings: Dict[int, List[tuple[Callable[[], Any], int, bool]]] = {}
        self.key_combinations: Dict[tuple[int, ...], Callable[[], Any]] = {}
        self.pressed_keys: Set[int] = set()
        self.event_handlers: List[Callable[[pygame.event.Event], None]] = []
    
    def bind_key(self, key: int, action: Callable[[], Any], priority: int = 0, continuous: bool = False) -> None:
        """Bind a key to an action."""
        if key not in self.key_bindings:
            self.key_bindings[key] = []
        self.key_bindings[key].append((action, priority, continuous))
        self.key_bindings[key].sort(key=lambda x: x[1], reverse=True)
    
    def bind_key_combination(self, keys: List[int], action: Callable[[], Any]) -> None:
        """Bind a key combination to an action."""
        self.key_combinations[tuple(sorted(keys))] = action
    
    def handle_keydown(self, key: int) -> None:
        """Handle key press event."""
        self.pressed_keys.add(key)
        
        # Check key combinations
        for combo_keys, action in self.key_combinations.items():
            if all(k in self.pressed_keys for k in combo_keys):
                action()
        
        # Handle individual key bindings
        if key in self.key_bindings:
            for action, _, _ in self.key_bindings[key]:
                if action() is True:  # Action returns True to block further processing
                    break
    
    def handle_keyup(self, key: int) -> None:
        """Handle key release event."""
        self.pressed_keys.discard(key)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame event."""
        for handler in self.event_handlers:
            handler(event)
    
    def add_event_handler(self, handler: Callable[[pygame.event.Event], None]) -> None:
        """Add event handler."""
        self.event_handlers.append(handler)
    
    def is_key_pressed(self, key: int) -> bool:
        """Check if a key is currently pressed."""
        return key in self.pressed_keys
    
    def update(self, dt: float) -> None:
        """Update input state."""
        # Handle continuous actions for held keys
        for key in self.pressed_keys:
            if key in self.key_bindings:
                for action, _, continuous in self.key_bindings[key]:
                    if continuous:
                        if action() is True:  # Action returns True to block further processing
                            break 

class ScreenWrapComponent(Component):
    """Component for wrapping entities around screen edges."""
    def __init__(self, entity):
        super().__init__(entity)
        self.wrap_x = True
        self.wrap_y = True
        self.buffer = 0  # Extra space before wrapping
    
    def update(self, dt: float) -> None:
        """Update screen wrapping."""
        transform = self.entity.get_component(TransformComponent)
        if not transform:
            return
        
        # Get screen dimensions from game instance
        width = self.entity.game.width
        height = self.entity.game.height
        
        # Wrap position
        if self.wrap_x:
            if transform.position.x < -self.buffer:
                transform.position.x = width + self.buffer
            elif transform.position.x > width + self.buffer:
                transform.position.x = -self.buffer
        
        if self.wrap_y:
            if transform.position.y < -self.buffer:
                transform.position.y = height + self.buffer
            elif transform.position.y > height + self.buffer:
                transform.position.y = -self.buffer 