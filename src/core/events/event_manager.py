"""Event manager singleton for handling game events."""
from typing import Dict, List, Callable
from .event import Event, EventType

class EventManager:
    """Singleton manager for handling game events."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the event manager."""
        self._listeners: Dict[EventType, List[Callable[[Event], None]]] = {}
        for event_type in EventType:
            self._listeners[event_type] = []
        print("Event manager initialized")  # Debug info

    def subscribe(self, event_type: EventType, listener: Callable[[Event], None]):
        """Subscribe to an event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)
        print(f"Subscribed to {event_type}")  # Debug info

    def unsubscribe(self, event_type: EventType, listener: Callable[[Event], None]):
        """Unsubscribe from an event type."""
        if event_type in self._listeners and listener in self._listeners[event_type]:
            self._listeners[event_type].remove(listener)
            print(f"Unsubscribed from {event_type}")  # Debug info

    def emit(self, event: Event):
        """Emit an event to all subscribed listeners."""
        if event.type in self._listeners:
            for listener in self._listeners[event.type]:
                try:
                    listener(event)
                except Exception as e:
                    print(f"Error in event listener: {e}")  # Debug info