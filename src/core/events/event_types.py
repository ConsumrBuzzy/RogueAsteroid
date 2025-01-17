from dataclasses import dataclass
from .event import Event, EventType
from typing import Any

@dataclass
class EntityCreatedEvent(Event):
    """Event emitted when a new entity is created."""
    def __init__(self, entity: Any):
        super().__init__(
            type=EventType.ENTITY_CREATED,
            source=entity,
            data={"entity": entity}
        )

@dataclass
class EntityDestroyedEvent(Event):
    """Event emitted when an entity is destroyed."""
    def __init__(self, entity: Any):
        super().__init__(
            type=EventType.ENTITY_DESTROYED,
            source=entity,
            data={"entity": entity}
        )

@dataclass
class CollisionEvent(Event):
    """Event emitted when two entities collide."""
    def __init__(self, entity1: Any, entity2: Any):
        super().__init__(
            type=EventType.COLLISION,
            data={
                "entity1": entity1,
                "entity2": entity2
            }
        )

@dataclass
class ScoreChangedEvent(Event):
    """Event emitted when the score changes."""
    def __init__(self, old_score: int, new_score: int):
        super().__init__(
            type=EventType.SCORE_CHANGED,
            data={
                "old_score": old_score,
                "new_score": new_score,
                "delta": new_score - old_score
            }
        )

@dataclass
class GameStateChangedEvent(Event):
    """Event emitted when the game state changes."""
    def __init__(self, old_state: Any, new_state: Any):
        super().__init__(
            type=EventType.GAME_STATE_CHANGED,
            data={
                "old_state": old_state,
                "new_state": new_state
            }
        )