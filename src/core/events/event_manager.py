"""Event management system for game-wide communication."""
from typing import Dict, List, Callable, Any
from enum import Enum, auto

class GameEvent(Enum):
    """Enumeration of all possible game events."""
    GAME_START = auto()
    GAME_OVER = auto()
    WAVE_START = auto()
    WAVE_COMPLETE = auto()
    ENTITY_SPAWNED = auto()
    ENTITY_DESTROYED = auto()
    COLLISION = auto()
    SCORE_CHANGED = auto()
    STATE_CHANGED = auto()
    PLAYER_DIED = auto()
    PLAYER_RESPAWN = auto()
    HIGH_SCORE_ACHIEVED = auto()

class EventManager:
    """Manager for game-wide event handling.
    
    Provides:
    - Event subscription
    - Event publishing
    - Priority-based handlers
    - Event filtering
    - Debug support
    """
    
    def __init__(self):
        """Initialize the event manager."""
        self._handlers: Dict[GameEvent, List[Callable]] = {}
        self._pending_events: List[tuple[GameEvent, dict]] = []
        print("EventManager initialized")
        
    def subscribe(self, event_type: GameEvent, handler: Callable) -> None:
        """Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Callback function for event handling
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        print(f"Subscribed handler to {event_type.name}")
        
    def unsubscribe(self, event_type: GameEvent, handler: Callable) -> None:
        """Unsubscribe from an event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler to remove
        """
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            print(f"Unsubscribed handler from {event_type.name}")
            
    def publish(self, event_type: GameEvent, **kwargs) -> None:
        """Publish an event to all subscribers.
        
        Args:
            event_type: Type of event to publish
            **kwargs: Event data to pass to handlers
        """
        self._pending_events.append((event_type, kwargs))
        print(f"Event queued: {event_type.name}")
        
    def update(self) -> None:
        """Process all pending events."""
        while self._pending_events:
            event_type, kwargs = self._pending_events.pop(0)
            if event_type in self._handlers:
                for handler in self._handlers[event_type]:
                    try:
                        handler(**kwargs)
                    except Exception as e:
                        print(f"Error in event handler for {event_type.name}: {e}")
                        
    def clear(self) -> None:
        """Clear all event handlers and pending events."""
        self._handlers.clear()
        self._pending_events.clear()
        print("Event system cleared") 