"""
Base components for the ECS system.
Components are pure data containers that can be attached to entities.
"""

from dataclasses import dataclass
from typing import Any
import pygame

@dataclass
class Component:
    """Base class for all components. All components should inherit from this."""
    pass

@dataclass
class Position(Component):
    """Component for storing entity position and rotation."""
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0

    @property
    def vec2(self) -> pygame.Vector2:
        """Get position as a pygame Vector2."""
        return pygame.Vector2(self.x, self.y)

@dataclass
class Velocity(Component):
    """Component for storing entity velocity."""
    dx: float = 0.0
    dy: float = 0.0
    angular: float = 0.0

    @property
    def vec2(self) -> pygame.Vector2:
        """Get velocity as a pygame Vector2."""
        return pygame.Vector2(self.dx, self.dy)

@dataclass
class Collider(Component):
    """Component for collision detection."""
    radius: float = 10.0
    mask: int = 0  # Collision mask for filtering
    active: bool = True

@dataclass
class Renderable(Component):
    """Component for renderable entities."""
    texture: Any = None  # pygame.Surface
    width: float = 0
    height: float = 0
    layer: int = 0  # Render layer (higher numbers render on top)
    visible: bool = True

@dataclass
class Input(Component):
    """Component for entities that receive input."""
    thrust: bool = False
    reverse: bool = False
    rotate_left: bool = False
    rotate_right: bool = False
    shoot: bool = False
