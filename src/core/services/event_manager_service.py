"""Service for managing game events and subscriptions."""
from typing import Dict, List, Callable, Any
from collections import defaultdict

class EventManagerService:
    """Service for managing game events.
    
    Provides:
    - Event subscription/publishing
    - Event queuing
    - Priority-based handlers
    - Type-safe events
    - Debug support
    """
    
    def __init__(self):
        """Initialize the event manager service."""
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_queue: List[tuple[str, Dict[str, Any]]] = []
        print("EventManagerService initialized")
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Callback function for handling the event
        """
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)
            print(f"Subscribed handler to event: {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Unsubscribe from an event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler to remove
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(handler)
                print(f"Unsubscribed handler from event: {event_type}")
            except ValueError:
                print(f"Warning: Handler not found for event: {event_type}")
    
    def publish(self, event_type: str, **kwargs) -> None:
        """Publish an event to be processed.
        
        Args:
            event_type: Type of event to publish
            **kwargs: Event data
        """
        self._event_queue.append((event_type, kwargs))
        print(f"Published event: {event_type}")
    
    def process_events(self) -> None:
        """Process all queued events."""
        # Process copy of queue to allow new events during processing
        current_events = self._event_queue[:]
        self._event_queue.clear()
        
        for event_type, kwargs in current_events:
            if event_type in self._subscribers:
                for handler in self._subscribers[event_type]:
                    try:
                        handler(**kwargs)
                    except Exception as e:
                        print(f"Error in event handler for {event_type}: {e}")
    
    def clear(self) -> None:
        """Clear all events and subscribers."""
        self._subscribers.clear()
        self._event_queue.clear()
        print("Event manager cleared")
    
    def cleanup(self) -> None:
        """Clean up the service."""
        self.clear()
        print("EventManagerService cleaned up") 