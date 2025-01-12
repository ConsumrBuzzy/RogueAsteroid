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
        self._max_queue_size = 1000  # Maximum events in queue
        self._processing = False  # Guard against recursive processing
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
        """Publish an event.
        
        Args:
            event_type: Type of event to publish
            **kwargs: Event data
        """
        if len(self._event_queue) >= self._max_queue_size:
            print(f"Warning: Event queue full, dropping event: {event_type}")
            return
        
        self._event_queue.append((event_type, kwargs))
        
    def process_events(self) -> None:
        """Process all queued events."""
        if self._processing:
            return  # Prevent recursive processing
        
        self._processing = True
        try:
            # Process up to max_queue_size events to prevent infinite loops
            for _ in range(min(len(self._event_queue), self._max_queue_size)):
                if not self._event_queue:
                    break
                
                event_type, kwargs = self._event_queue.pop(0)
                if event_type in self._subscribers:
                    for handler in self._subscribers[event_type][:]:  # Copy list to allow modification during iteration
                        try:
                            handler(**kwargs)
                        except Exception as e:
                            print(f"Error in event handler for {event_type}: {e}")
                            # Continue processing other handlers
                        
        finally:
            self._processing = False
    
    def clear(self) -> None:
        """Clear all events and subscribers."""
        self._subscribers.clear()
        self._event_queue.clear()
        print("Event manager cleared")
    
    def cleanup(self) -> None:
        """Clean up the event manager."""
        self._subscribers.clear()
        self._event_queue.clear()
        print("EventManagerService cleaned up") 