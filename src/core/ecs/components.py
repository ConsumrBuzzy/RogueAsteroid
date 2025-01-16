"""
Component classes for the ECS architecture.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import pygame

@dataclass
class Component:
    """Base class for all components."""
    pass

@dataclass
class Position:
    """Component for storing entity position and rotation."""
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0  # In degrees

@dataclass
class Velocity:
    """Component for storing entity velocity."""
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0  # Angular velocity in degrees/second

@dataclass
class Input:
    """Component for handling entity input."""
    up: bool = False
    down: bool = False
    left: bool = False
    right: bool = False
    fire: bool = False

@dataclass
class Renderable:
    """Component for rendering entities."""
    sprite_name: str = ""  # Name of sprite or shape to use
    visible: bool = True
    color: Tuple[int, int, int] = (255, 255, 255)  # RGB color
    rotation: float = 0.0  # In degrees
    layer: int = 0  # Render layer (higher = on top)
    alpha: int = 255  # Transparency (0-255)
    size: float = 1.0  # For particle rendering
    line_width: int = 1  # Line width for vector shapes
    sprite: Optional[pygame.Surface] = None  # Cached sprite surface
    shape: Optional[List[Tuple[float, float]]] = None  # Cached vector shape

@dataclass
class Collider:
    """Component for collision detection."""
    radius: float = 1.0  # Collision radius

@dataclass
class Physics:
    """Component for physics simulation."""
    mass: float = 1.0
    max_speed: float = 500.0
    friction: float = 0.0
    thrust: float = 0.0

@dataclass
class Player:
    """Component for player-specific data."""
    lives: int = 3
    score: int = 0
    invulnerable: bool = False
    invulnerable_timer: float = 0.0
    shoot_cooldown: float = 0.0

@dataclass
class Bullet:
    """Component for bullet-specific data."""
    lifetime: float = 0.5
    damage: int = 1

@dataclass
class Asteroid:
    """Component for asteroid-specific data."""
    size: str = "large"  # large, medium, or small
    points: int = 0

@dataclass
class Particle:
    """Component for particle effects."""
    lifetime: float = 1.0
    time_alive: float = 0.0
