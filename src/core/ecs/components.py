"""
Core components for the ECS architecture.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
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
class Physics:
    """Component for physics simulation."""
    mass: float = 1.0
    max_speed: float = 500.0
    friction: float = 0.0
    thrust: float = 200.0  # Thrust force when accelerating
    drag: float = 0.1  # Air resistance

@dataclass
class Input:
    """Component for handling entity input."""
    up: bool = False  # Thrust
    down: bool = False  # Reverse thrust
    left: bool = False  # Rotate left
    right: bool = False  # Rotate right
    fire: bool = False  # Fire weapon

@dataclass
class Renderable:
    """Component for rendering entities."""
    sprite_name: str = ""  # Name of sprite or shape to use
    visible: bool = True
    color: Tuple[int, int, int] = (255, 255, 255)  # RGB color
    rotation: float = 0.0  # In degrees
    layer: int = 0  # Render layer (higher = on top)
    alpha: int = 255  # Transparency (0-255)
    size: float = 1.0  # Scale factor or particle size
    line_width: int = 1  # Line width for vector shapes
    sprite: Optional[pygame.Surface] = None  # Cached sprite surface
    shape: Optional[List[Tuple[float, float]]] = None  # Cached vector shape
    blink: bool = False  # For invulnerability effect
    blink_timer: float = 0.0  # Timer for blink effect
    blink_rate: float = 0.1  # How fast to blink

@dataclass
class Collider:
    """Component for collision detection."""
    radius: float = 1.0  # Collision radius
    active: bool = True  # Whether collision is active
    mask: int = 0xFFFFFFFF  # Collision mask for filtering

@dataclass
class Player:
    """Component for player-specific data."""
    lives: int = 3
    score: int = 0
    invulnerable: bool = False
    invulnerable_timer: float = 0.0
    shoot_cooldown: float = 0.0
    max_shoot_cooldown: float = 0.2  # Time between shots

@dataclass
class Bullet:
    """Component for bullet-specific data."""
    lifetime: float = 0.5
    damage: int = 1
    speed: float = 800.0

@dataclass
class Asteroid:
    """Component for asteroid-specific data."""
    size: str = "large"  # large, medium, or small
    points: int = 0
    split_count: int = 2  # Number of pieces to split into
    health: int = 1

@dataclass
class Particle:
    """Component for particle effects."""
    lifetime: float = 1.0
    time_alive: float = 0.0
    color: Tuple[int, int, int] = (255, 255, 255)
    fade: bool = True  # Whether to fade out over lifetime
    size: float = 1.0
    shrink: bool = False  # Whether to shrink over lifetime

@dataclass
class Sound:
    """Component for entity sound effects."""
    sounds: Dict[str, pygame.mixer.Sound] = field(default_factory=dict)
    volume: float = 1.0
    playing: bool = False

@dataclass
class Menu:
    """Component for menu items."""
    text: str = ""
    selected: bool = False
    action: Optional[str] = None
    position: Tuple[float, float] = (0, 0)
    size: Tuple[float, float] = (0, 0)
    color: Tuple[int, int, int] = (255, 255, 255)
    hover_color: Tuple[int, int, int] = (255, 255, 0)
    font_size: int = 32
