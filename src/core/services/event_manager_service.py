"""Service for managing game events and subscriptions."""
from typing import Dict, List, Callable, Any
from collections import defaultdict
import pygame

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
        if len(self._event_queue) < self._max_queue_size:
            self._event_queue.append((event_type, kwargs))
        else:
            print("Warning: Event queue full, dropping event:", event_type)
            
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a pygame event.
        
        Args:
            event: Pygame event to handle
        """
        # Convert pygame event to game event
        event_type = pygame.event.event_name(event.type)
        
        # Create event data from pygame event attributes
        event_data = {}
        if hasattr(event, 'pos'):
            event_data['pos'] = event.pos
        if hasattr(event, 'key'):
            event_data['key'] = event.key
        if hasattr(event, 'mod'):
            event_data['mod'] = event.mod
        if hasattr(event, 'button'):
            event_data['button'] = event.button
            
        # Publish event
        self.publish(event_type, **event_data)
        
        # Process immediately
        self.process_events()
            
    def process_events(self) -> None:
        """Process all queued events."""
        if self._processing:
            return  # Prevent recursive processing
            
        self._processing = True
        try:
            while self._event_queue:
                event_type, event_data = self._event_queue.pop(0)
                for handler in self._subscribers[event_type]:
                    try:
                        handler(event_type, **event_data)
                    except Exception as e:
                        print(f"Error in event handler for {event_type}: {e}")
        finally:
            self._processing = False
            
    def clear(self) -> None:
        """Clear all queued events."""
        self._event_queue.clear()
        
    def cleanup(self) -> None:
        """Clean up the service."""
        self.clear()
        self._subscribers.clear()
        print("EventManagerService cleaned up") 