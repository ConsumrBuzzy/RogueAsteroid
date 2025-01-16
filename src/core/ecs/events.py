"""
Event system for entity communication.
"""

from dataclasses import dataclass
from typing import Dict, List, Type, Callable, TypeVar
from collections import defaultdict

@dataclass
class Event:
    """Base class for all events."""
    pass

@dataclass
class CollisionEvent(Event):
    """Fired when two entities collide."""
    entity1: int
    entity2: int

@dataclass
class EntityDestroyedEvent(Event):
    """Fired when an entity is destroyed."""
    entity: int

@dataclass
class ScoreEvent(Event):
    """Fired when points are scored."""
    points: int
    entity: int

T = TypeVar('T', bound=Event)

class EventManager:
    """
    Handles event subscription and emission.
    Allows for decoupled communication between systems.
    """
    def __init__(self):
        self._handlers: Dict[Type[Event], List[Callable]] = defaultdict(list)
        self._pending_events: List[Event] = []

    def emit(self, event: Event) -> None:
        """Queue an event for processing."""
        self._pending_events.append(event)

    def subscribe(self, event_type: Type[T], handler: Callable[[T], None]) -> None:
        """Subscribe to an event type."""
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: Type[Event], handler: Callable) -> None:
        """Unsubscribe from an event type."""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)

    def process_events(self) -> None:
        """Process all pending events."""
        # Create a local copy and clear pending events
        events = self._pending_events[:]
        self._pending_events.clear()

        # Process each event
        for event in events:
            event_type = type(event)
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    # In a real game, you'd want proper error handling here
                    print(f"Error processing event {event_type.__name__}: {e}")

    def clear(self) -> None:
        """Clear all event handlers and pending events."""
        self._handlers.clear()
        self._pending_events.clear()
