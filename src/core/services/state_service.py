"""State service for game state management."""
from typing import Optional, Dict, Callable, Set, List
import pygame
from ..state.game_states import GameState
from .logging_service import LoggingService

class StateService:
    """Service for managing game states.
    
    Provides:
    - State transitions
    - State-specific updates
    - Menu state handling
    """
    
    _instance = None
    
    def __new__(cls):
        """Create or return singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
            cls._instance._ready = False  # Add ready flag
        return cls._instance
        
    def __init__(self):
        """Initialize the state service."""
        if self._initialized:
            return
            
        self._current_state: Optional[GameState] = None
        self._previous_state: Optional[GameState] = None
        self._state_handlers: Dict[GameState, Callable] = {}
        self._event_manager = None  # Will be set by set_event_manager
        self._valid_transitions: Dict[GameState, Set[GameState]] = {}
        self._subscribers: Dict[str, List[Callable]] = {}
        self._logger = LoggingService()
        self._ready = False  # Ensure not ready during initialization
        
        try:
            # Initialize valid transitions
            self._setup_valid_transitions()
            
            # Set initial state without triggering handlers
            self._current_state = GameState.MAIN_MENU
            self._logger.log("StateService initialized", "INFO")
            self._initialized = True
            self._ready = True  # Mark as ready after successful initialization
        except Exception as e:
            self._logger.log(f"Failed to initialize StateService: {e}", "ERROR")
            raise
        
    def _setup_valid_transitions(self) -> None:
        """Setup valid state transitions."""
        # Define valid transitions from each state
        self.add_valid_transition(None, GameState.MAIN_MENU)  # Initial transition
        self.add_valid_transition(GameState.MAIN_MENU, GameState.PLAYING)
        self.add_valid_transition(GameState.MAIN_MENU, GameState.OPTIONS)
        self.add_valid_transition(GameState.MAIN_MENU, GameState.HIGH_SCORES)
        self.add_valid_transition(GameState.MAIN_MENU, GameState.QUIT)
        
        self.add_valid_transition(GameState.PLAYING, GameState.PAUSED)
        self.add_valid_transition(GameState.PLAYING, GameState.GAME_OVER)
        
        self.add_valid_transition(GameState.PAUSED, GameState.PLAYING)
        self.add_valid_transition(GameState.PAUSED, GameState.MAIN_MENU)
        
        self.add_valid_transition(GameState.GAME_OVER, GameState.MAIN_MENU)
        self.add_valid_transition(GameState.GAME_OVER, GameState.PLAYING)  # For restart
        
        self.add_valid_transition(GameState.OPTIONS, GameState.MAIN_MENU)
        self.add_valid_transition(GameState.HIGH_SCORES, GameState.MAIN_MENU)
        
        self._logger.log("State transitions initialized", "DEBUG")
        
    def register_handler(self, state: GameState, handler: Callable) -> None:
        """Register a handler for a state.
        
        Args:
            state: Game state to handle
            handler: Function to call when state is active
            
        Raises:
            ValueError: If state or handler is invalid
            RuntimeError: If handler registration fails
        """
        if not isinstance(state, GameState):
            raise ValueError(f"Invalid state type: {type(state)}")
        if not callable(handler):
            raise ValueError("Handler must be callable")
            
        try:
            # Validate handler interface
            if hasattr(handler, 'on_enter') and not callable(handler.on_enter):
                raise ValueError("on_enter must be callable")
            if hasattr(handler, 'on_exit') and not callable(handler.on_exit):
                raise ValueError("on_exit must be callable")
                
            # Test handler call without actually executing it
            if not hasattr(handler, '__call__'):
                raise RuntimeError("Handler must be callable")
                
            self._state_handlers[state] = handler
            self._logger.log(f"Registered handler for state {state.name}", "INFO")
            
        except Exception as e:
            error_msg = f"Error registering handler for state {state.name}: {e}"
            self._logger.log(error_msg, "ERROR")
            raise
        
    def set_event_manager(self, event_manager) -> None:
        """Set the event manager for state change notifications.
        
        Args:
            event_manager: EventManagerService instance
        """
        self._event_manager = event_manager
        self._logger.log("Event manager connected to state service", "INFO")
        
        # Now that we have the event manager, publish initial state
        if self._current_state:
            self._event_manager.publish('state_changed', 
                old_state=None,
                new_state=self._current_state)
            self._logger.log(f"Published initial state: {self._current_state}", "DEBUG")

    def add_valid_transition(self, from_state: GameState, to_state: GameState) -> None:
        """Add a valid state transition.
        
        Args:
            from_state: Starting state
            to_state: Target state
        """
        if from_state not in self._valid_transitions:
            self._valid_transitions[from_state] = set()
        self._valid_transitions[from_state].add(to_state)

    def is_valid_transition(self, from_state: GameState, to_state: GameState) -> bool:
        """Check if a state transition is valid.
        
        Args:
            from_state: Starting state
            to_state: Target state
            
        Returns:
            True if transition is valid
        """
        # Allow any transition if no valid transitions defined
        if not self._valid_transitions:
            return True
        
        # Allow transition to same state
        if from_state == to_state:
            return True
        
        # Check if transition is explicitly allowed
        return to_state in self._valid_transitions.get(from_state, set())

    def change_state(self, new_state: GameState) -> None:
        """Change to a new game state.
        
        Args:
            new_state: State to change to
            
        Raises:
            ValueError: If new_state is invalid or service not ready
            RuntimeError: If state transition fails
        """
        if not self._ready:
            raise ValueError("StateService not ready for state changes")
            
        if not isinstance(new_state, GameState):
            raise ValueError(f"Invalid state type: {type(new_state)}")
            
        if new_state == self._current_state:
            return
            
        # Validate transition
        if not self.is_valid_transition(self._current_state, new_state):
            raise ValueError(f"Invalid state transition from {self._current_state} to {new_state}")
            
        try:
            # Store states for potential rollback
            old_state = self._current_state
            old_previous = self._previous_state
            
            # Call exit handler for current state if it exists
            if self._current_state and self._current_state in self._state_handlers:
                handler = self._state_handlers[self._current_state]
                if hasattr(handler, 'on_exit'):
                    try:
                        handler.on_exit()
                    except Exception as e:
                        print(f"Error in exit handler for state {self._current_state.name}: {e}")
                        # Continue with transition but log the error
                    
            self._previous_state = self._current_state
            self._current_state = new_state
            
            # Notify state change through event manager first
            if self._event_manager:
                self._event_manager.publish('state_changed', 
                    old_state=self._previous_state,
                    new_state=self._current_state)
                self._logger.log(f"Published state change event: {self._previous_state} -> {new_state}", "DEBUG")
                    
            # Then notify direct subscribers
            for subscriber_id, callbacks in self._subscribers.items():
                for callback in callbacks:
                    try:
                        callback(old_state=self._previous_state, new_state=self._current_state)
                    except Exception as e:
                        error_msg = f"Error in state change callback for {subscriber_id}: {e}"
                        self._logger.log(error_msg, "ERROR")
                        continue
            
            self._logger.log(f"Changed state from {self._previous_state} to {new_state}", "INFO")
            
            # Call enter handler for new state if it exists
            if new_state in self._state_handlers:
                handler = self._state_handlers[new_state]
                if hasattr(handler, 'on_enter'):
                    try:
                        handler.on_enter()
                    except Exception as e:
                        error_msg = f"Error in enter handler for state {new_state.name}: {e}"
                        self._logger.log(error_msg, "ERROR")
                        # Rollback state change
                        self._current_state = old_state
                        self._previous_state = old_previous
                        raise RuntimeError(f"Failed to enter state {new_state.name}: {e}")
                    
        except Exception as e:
            error_msg = f"Error during state transition: {e}"
            self._logger.log(error_msg, "ERROR")
            # Ensure state is valid even if transition fails
            if self._current_state is None:
                self._logger.log("Critical error: Reverting to MAIN_MENU", "ERROR")
                self._current_state = GameState.MAIN_MENU
            raise
            
    def get_current_state(self) -> Optional[GameState]:
        """Get the current game state.
        
        Returns:
            Current GameState or None
        """
        return self._current_state
        
    def get_previous_state(self) -> Optional[GameState]:
        """Get the previous game state.
        
        Returns:
            Previous GameState or None
        """
        return self._previous_state
        
    def update(self, dt: float) -> None:
        """Update current state.
        
        Args:
            dt: Delta time in seconds
            
        Raises:
            RuntimeError: If state update fails critically
        """
        if not self._current_state:
            print("Warning: No current state")
            return
            
        try:
            if self._current_state in self._state_handlers:
                handler = self._state_handlers[self._current_state]
                try:
                    # Call the handler with delta time
                    handler(dt)
                except Exception as e:
                    print(f"Error updating state {self._current_state.name}: {e}")
                    # Consider changing to a safe state on critical errors
                    if isinstance(e, (RuntimeError, SystemError)):
                        print("Critical error, reverting to main menu")
                        self.change_state(GameState.MAIN_MENU)
                        raise RuntimeError(f"Critical error in state {self._current_state.name}: {e}")
                        
        except Exception as e:
            print(f"Error in state update: {e}")
            # Continue running but log the error
            
    def cleanup(self) -> None:
        """Clean up the state service."""
        if not getattr(self, '_ready', False):
            if hasattr(self, '_logger'):
                self._logger.log("Cleanup called before service was ready", "WARNING")
            return
            
        # Clear subscribers
        if hasattr(self, '_subscribers'):
            self._subscribers.clear()
        
        # Clear handlers
        if hasattr(self, '_state_handlers'):
            self._state_handlers.clear()
        
        # Clear state
        self._current_state = None
        self._previous_state = None
        
        self._ready = False  # Mark as not ready after cleanup
        if hasattr(self, '_logger'):
            self._logger.log("StateService cleaned up", "INFO")
        print("StateService cleaned up")

    def subscribe(self, subscriber_id: str, callback: Callable) -> None:
        """Subscribe to state changes.
        
        Args:
            subscriber_id: Unique identifier for the subscriber
            callback: Function to call on state changes
            
        Raises:
            ValueError: If subscriber_id is empty or callback is not callable
        """
        if not subscriber_id:
            raise ValueError("Subscriber ID cannot be empty")
        if not callable(callback):
            raise ValueError("Callback must be callable")
            
        if subscriber_id not in self._subscribers:
            self._subscribers[subscriber_id] = []
        self._subscribers[subscriber_id].append(callback)
        
    def unsubscribe(self, subscriber_id: str) -> None:
        """Unsubscribe from state changes.
        
        Args:
            subscriber_id: Unique identifier for the subscriber
        """
        if subscriber_id in self._subscribers:
            del self._subscribers[subscriber_id]
            
    def _notify_subscribers(self, event_type: str, **kwargs) -> None:
        """Notify subscribers of state changes.
        
        Args:
            event_type: Type of event that occurred
            **kwargs: Event data including old_state and new_state
        """
        # This method is now deprecated in favor of direct notification
        # Kept for backward compatibility
        pass

    def is_ready(self) -> bool:
        """Check if service is fully initialized and ready.
        
        Returns:
            True if service is ready for use
        """
        return self._ready