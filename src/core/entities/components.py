"""Additional components for game entities."""
import pygame
import numpy as np
from typing import Dict, List, Tuple, Callable, Optional
from src.core.entities.base import Component, Entity, TransformComponent
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT

class ScreenWrapComponent(Component):
    """Component that handles screen wrapping for entities."""

    def __init__(self, width: int, height: int):
        """Initialize screen wrap component.
        
        Args:
            width: Screen width
            height: Screen height
        """
        super().__init__()
        self.width = width
        self.height = height
        print(f"ScreenWrap initialized with width={width}, height={height}")  # Debug info

    def update(self):
        """Update entity position to wrap around screen edges."""
        transform = self.entity.get_component('transform')
        if not transform:
            return
        
        # Wrap horizontally
        if transform.position.x < 0:
            transform.position.x = self.width
        elif transform.position.x > self.width:
            transform.position.x = 0
        
        # Wrap vertically
        if transform.position.y < 0:
            transform.position.y = self.height
        elif transform.position.y > self.height:
            transform.position.y = 0

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
            transform.velocity += acceleration * dt
        
        # Apply friction
        if self.friction > 0:
            transform.velocity *= (1.0 - self.friction)
        
        # Limit speed
        if self.max_speed is not None:
            speed = np.linalg.norm(transform.velocity)
            if speed > self.max_speed:
                transform.velocity = (transform.velocity / speed) * self.max_speed
        
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
        self.lifetime = lifetime
        self.time_remaining = lifetime  # Separate tracker for remaining time
        self.color = color
        self.alpha = 255  # For fade out effect
        self.size = 2.0  # Particle size in pixels
        
    def update(self, dt: float) -> None:
        """Update the particle state."""
        if not self.entity or not self.entity.game:
            return
            
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            # Remove from game entities list if it exists
            if self.entity in self.entity.game.entities:
                self.entity.game.entities.remove(self.entity)
            return

        # Update alpha for fade out (ensure it stays between 0 and 255)
        self.alpha = max(0, min(255, int((self.time_remaining / self.lifetime) * 255)))

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