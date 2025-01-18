"""Additional components for game entities."""
import pygame
import numpy as np
from typing import Dict, List, Tuple, Callable, Optional
from src.core.entities.base import Component, Entity, TransformComponent
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from src.core.utils import to_vector2, ensure_minimum_velocity

class ScreenWrapComponent(Component):
    """Component for wrapping entities around screen edges."""
    
    def __init__(self, entity, width=WINDOW_WIDTH, height=WINDOW_HEIGHT):
        """Initialize the screen wrap component.
        
        Args:
            entity: The entity this component belongs to
            width: Screen width to wrap at
            height: Screen height to wrap at
        """
        super().__init__(entity)
        self.width = width
        self.height = height
        self.wrap_offset = 2  # 2 pixel offset for minimal edge overlap
        print(f"ScreenWrap initialized with width={width}, height={height}")  # Debug info
    
    def update(self, dt: float) -> None:
        """Update entity position to wrap around screen."""
        transform = self.entity.get_component('transform')
        if not transform:
            return
        
        # Wrap x position with minimal offset
        if transform.position[0] <= -self.wrap_offset:
            transform.position[0] = self.width - self.wrap_offset
        elif transform.position[0] >= self.width + self.wrap_offset:
            transform.position[0] = self.wrap_offset
        
        # Wrap y position with minimal offset
        if transform.position[1] <= -self.wrap_offset:
            transform.position[1] = self.height - self.wrap_offset
        elif transform.position[1] >= self.height + self.wrap_offset:
            transform.position[1] = self.wrap_offset

class InputComponent(Component):
    """Component for handling input."""
    
    def __init__(self, entity: Entity):
        super().__init__(entity)
        self.key_bindings = {}  # Key -> (callback, continuous) mapping
        self.active_keys = set()  # Currently pressed keys
    
    def bind_key(self, key, callback, continuous=False):
        """Bind a key to a callback function."""
        self.key_bindings[key] = (callback, continuous)
    
    def clear_bindings(self):
        """Clear all key bindings."""
        self.key_bindings.clear()
        self.active_keys.clear()
    
    def handle_keydown(self, key):
        """Handle key press event."""
        if key in self.key_bindings:
            callback, continuous = self.key_bindings[key]
            if continuous:
                self.active_keys.add(key)
            else:
                callback()
    
    def handle_keyup(self, key):
        """Handle key release event."""
        if key in self.active_keys:
            self.active_keys.remove(key)
    
    def update(self, dt):
        """Update continuous key actions."""
        for key in self.active_keys:
            if key in self.key_bindings:
                callback, continuous = self.key_bindings[key]
                if continuous:
                    callback()

class PhysicsComponent(Component):
    """Component for physics-based movement."""
    
    def __init__(self, entity: Entity, mass: float = 1.0, max_speed: Optional[float] = None):
        super().__init__(entity)
        self.mass = mass
        self.max_speed = max_speed
        self.force = np.array([0.0, 0.0])
        self.friction = 0.0  # 0 to 1, applied each frame
        self.min_speed = 50.0  # Minimum speed to maintain
    
    def apply_force(self, force: np.ndarray) -> None:
        """Apply a force to the entity."""
        self.force += force
    
    def update(self, dt: float) -> None:
        """Update physics state."""
        transform = self.entity.get_component('transform')
        if not transform:
            return
        
        # Apply forces
        if self.mass > 0:
            acceleration = self.force / self.mass
            # Convert numpy array to pygame Vector2 for velocity update
            accel_vec = to_vector2(acceleration)
            transform.velocity += accel_vec * dt
        
        # Apply friction
        if self.friction > 0:
            transform.velocity *= (1.0 - self.friction)
        
        # Ensure minimum speed is maintained
        transform.velocity = ensure_minimum_velocity(transform.velocity, self.min_speed)
        
        # Limit speed
        if self.max_speed is not None:
            current_speed = transform.velocity.length()
            if current_speed > self.max_speed:
                transform.velocity = transform.velocity.normalize() * self.max_speed
        
        # Reset forces
        self.force = np.array([0.0, 0.0])

class EffectComponent(Component):
    """Component for visual effects."""
    
    class Effect:
        """Visual effect definition."""
        def __init__(self, vertices: List[Tuple[float, float]], 
                     color: Tuple[int, int, int],
                     offset: Tuple[float, float] = (0, 0)):
            self.vertices = vertices
            self.color = color
            self.offset = offset
            self.active = False
    
    def __init__(self, entity: Entity):
        super().__init__(entity)
        self.effects: Dict[str, EffectComponent.Effect] = {}
    
    def add_effect(self, name: str, vertices: List[Tuple[float, float]], 
                  color: Tuple[int, int, int],
                  offset: Tuple[float, float] = (0, 0)) -> None:
        """Add a new visual effect."""
        self.effects[name] = EffectComponent.Effect(vertices, color, offset)
    
    def set_effect_active(self, name: str, active: bool) -> None:
        """Set whether an effect is active."""
        if name in self.effects:
            self.effects[name].active = active
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw active effects."""
        transform = self.entity.get_component('transform')
        if not transform:
            return
        
        for effect in self.effects.values():
            if not effect.active:
                continue
            
            # Transform vertices
            screen_vertices = []
            angle = np.radians(transform.rotation)
            cos_a = np.cos(angle)
            sin_a = np.sin(angle)
            
            for x, y in effect.vertices:
                # Apply offset
                x += effect.offset[0]
                y += effect.offset[1]
                
                # Rotate
                rx = x * cos_a - y * sin_a
                ry = x * sin_a + y * cos_a
                
                # Translate to position
                screen_x = transform.position[0] + rx
                screen_y = transform.position[1] + ry
                screen_vertices.append((int(screen_x), int(screen_y)))
            
            # Draw effect
            if len(screen_vertices) >= 3:
                pygame.draw.polygon(surface, effect.color, screen_vertices) 

class ParticleComponent(Component):
    """Component for managing particle effects."""
    
    def __init__(self, entity: Entity = None, lifetime: float = 1.0, color: tuple = (255, 255, 255)):
        """Initialize the particle component.
        
        Args:
            entity: The entity this component belongs to
            lifetime: How long the particle lives in seconds
            color: RGB color tuple for the particle
        """
        super().__init__(entity)
        self.lifetime = max(0.1, min(lifetime, 2.0))  # Clamp between 0.1 and 2.0 seconds
        self.time_remaining = self.lifetime
        self.color = color
        self.alpha = 255
        self.size = 2.0
        print(f"Created particle with lifetime={self.lifetime:.2f}s")
        
    def is_expired(self) -> bool:
        """Check if the particle has expired.
        
        Returns:
            True if the particle's lifetime has ended, False otherwise.
        """
        return self.time_remaining <= 0
        
    def update(self, dt: float):
        """Update the particle state."""
        if not self.entity or not self.entity.game:
            return
            
        # Update time remaining
        self.time_remaining = max(0, self.time_remaining - dt)
        
        # Handle expiration
        if self.is_expired():
            if self.entity in self.entity.game.entities:
                print(f"Removing expired particle at {self.time_remaining:.2f}s")
                self.entity.game.entities.remove(self.entity)
            return

        # Update alpha for fade out
        fade_factor = self.time_remaining / self.lifetime
        self.alpha = max(0, min(255, int(fade_factor * 255)))
        
        # Gradually reduce size
        self.size = max(1.0, self.size * (0.95 ** (dt * 60)))  # Shrink over time
        
    def draw(self, screen: pygame.Surface):
        """Draw the particle."""
        if not self.entity:
            return
            
        transform = self.entity.get_component('transform')
        if not transform:
            return
            
        # Get position as integers for drawing
        if hasattr(transform.position, 'x'):
            pos_x = int(transform.position.x)
            pos_y = int(transform.position.y)
        else:
            pos_x = int(transform.position[0])
            pos_y = int(transform.position[1])
            
        # Create a surface with per-pixel alpha
        size_int = max(1, int(self.size * 2))  # Ensure minimum size of 1
        particle_surface = pygame.Surface((size_int, size_int), pygame.SRCALPHA)
        
        # Draw the particle with current alpha
        color_with_alpha = (*self.color, self.alpha)
        pygame.draw.circle(
            particle_surface,
            color_with_alpha,
            (int(self.size), int(self.size)),
            max(1, int(self.size))  # Ensure minimum radius of 1
        )
        
        # Draw to screen at integer positions
        screen.blit(particle_surface, (pos_x - int(self.size), pos_y - int(self.size))) 