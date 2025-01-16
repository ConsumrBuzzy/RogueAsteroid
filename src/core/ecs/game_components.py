"""
Game-specific components for the Rogue Asteroid game.
"""

from dataclasses import dataclass
from enum import Enum, auto
from .components import Component

class EntityType(Enum):
    """Types of game entities."""
    PLAYER = auto()
    ASTEROID = auto()
    BULLET = auto()
    PARTICLE = auto()

@dataclass
class Player(Component):
    """Component for player-specific data."""
    lives: int = 3
    invulnerable: bool = False
    invulnerable_timer: float = 0.0
    respawn_timer: float = 0.0

@dataclass
class Asteroid(Component):
    """Component for asteroid-specific data."""
    size: str = "large"  # large, medium, or small
    points: int = 50
    split_count: int = 2  # Number of smaller asteroids to create when destroyed

@dataclass
class Bullet(Component):
    """Component for bullet-specific data."""
    lifetime: float = 0.5  # Time in seconds before bullet despawns
    damage: int = 1

@dataclass
class Score(Component):
    """Component for scoring."""
    value: int = 0
    multiplier: float = 1.0

@dataclass
class Lifetime(Component):
    """Component for entities with limited lifetime."""
    total: float  # Total lifetime in seconds
    remaining: float  # Remaining lifetime in seconds

@dataclass
class Physics(Component):
    """Extended physics properties."""
    mass: float = 1.0
    drag: float = 0.0
    max_speed: float = 500.0
    max_rotation: float = 360.0  # Degrees per second

@dataclass
class EntityTag(Component):
    """Component for identifying entity types."""
    type: EntityType
    name: str = ""  # Optional name for the entity
