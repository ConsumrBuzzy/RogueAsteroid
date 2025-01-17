"""Base event system classes."""
from dataclasses import dataclass
from typing import Any
from enum import Enum, auto

class EventType(Enum):
    """Types of events that can occur in the game."""
    ENTITY_CREATED = auto()
    ENTITY_DESTROYED = auto()
    COLLISION = auto()
    SCORE_CHANGED = auto()
    GAME_STATE_CHANGED = auto()
    PLAYER_DAMAGED = auto()
    POWERUP_COLLECTED = auto()

@dataclass
class Event:
    """Base class for all game events."""
    type: EventType
    source: Any = None
    data: dict = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}