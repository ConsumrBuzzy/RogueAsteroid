"""Additional components for game entities."""
import pygame
import numpy as np
from typing import Dict, Any, Callable, Set
from .base import Component, TransformComponent

class ScreenWrapComponent(Component):
    """Handles screen wrapping behavior."""
    
    def __init__(self, entity: 'Entity', width: float, height: float):
        super().__init__(entity)
        self.width = width
        self.height = height
    
    def update(self, dt: float) -> None:
        """Wrap position around screen edges."""
        transform = self.entity.get_component(TransformComponent)
        if not transform:
            return
            
        transform.position[0] %= self.width
        transform.position[1] %= self.height

class InputComponent(Component):
    """Handles entity input processing."""
    
    def __init__(self, entity: 'Entity'):
        super().__init__(entity)
        self.bindings: Dict[int, Callable] = {}
        self.continuous_bindings: Dict[int, Callable] = {}
        self.active_keys: Set[int] = set()
    
    def bind_key(self, key: int, action: Callable, continuous: bool = False) -> None:
        """Bind a key to an action."""
        if continuous:
            self.continuous_bindings[key] = action
        else:
            self.bindings[key] = action
    
    def handle_keydown(self, key: int) -> None:
        """Handle key press event."""
        self.active_keys.add(key)
        if key in self.bindings:
            self.bindings[key]()
    
    def handle_keyup(self, key: int) -> None:
        """Handle key release event."""
        self.active_keys.discard(key)
    
    def update(self, dt: float) -> None:
        """Process continuous key inputs."""
        for key, action in self.continuous_bindings.items():
            if key in self.active_keys:
                action()

class PhysicsComponent(Component):
    """Handles physics-based movement."""
    
    def __init__(self, entity: 'Entity', mass: float = 1.0, max_speed: float = float('inf')):
        super().__init__(entity)
        self.mass = mass
        self.max_speed = max_speed
        self.forces = np.array([0.0, 0.0])
        self.friction = 1.0  # No friction by default
    
    def apply_force(self, force: np.ndarray) -> None:
        """Apply a force to the entity."""
        self.forces += force
    
    def update(self, dt: float) -> None:
        """Update physics state."""
        transform = self.entity.get_component(TransformComponent)
        if not transform:
            return
        
        # Apply forces
        acceleration = self.forces / self.mass
        transform.velocity += acceleration * dt
        
        # Apply friction
        transform.velocity *= self.friction
        
        # Limit speed
        speed = np.linalg.norm(transform.velocity)
        if speed > self.max_speed:
            transform.velocity = (transform.velocity / speed) * self.max_speed
        
        # Reset forces
        self.forces = np.array([0.0, 0.0])

class EffectComponent(Component):
    """Handles visual effects like thrust flames, explosions, etc."""
    
    def __init__(self, entity: 'Entity'):
        super().__init__(entity)
        self.effects: Dict[str, Dict[str, Any]] = {}
    
    def add_effect(self, name: str, vertices: list, color: tuple, 
                  offset: tuple = (0, 0), active: bool = False) -> None:
        """Add a new visual effect."""
        self.effects[name] = {
            'vertices': vertices,
            'color': color,
            'offset': np.array(offset),
            'active': active
        }
    
    def set_effect_active(self, name: str, active: bool) -> None:
        """Set whether an effect is active."""
        if name in self.effects:
            self.effects[name]['active'] = active
    
    def draw(self, surface: Any) -> None:
        """Draw active effects."""
        transform = self.entity.get_component(TransformComponent)
        if not transform:
            return
            
        for effect in self.effects.values():
            if not effect['active']:
                continue
                
            # Transform effect vertices
            angle_rad = np.radians(transform.rotation)
            cos_rot = np.cos(angle_rad)
            sin_rot = np.sin(angle_rad)
            
            transformed = []
            for x, y in effect['vertices']:
                # Apply offset
                px = x + effect['offset'][0]
                py = y + effect['offset'][1]
                # Rotate
                rx = px * cos_rot - py * sin_rot
                ry = px * sin_rot + py * cos_rot
                # Translate
                rx += transform.position[0]
                ry += transform.position[1]
                transformed.append((rx, ry))
            
            # Draw effect
            pygame.draw.polygon(surface, effect['color'], transformed) 