"""State service for game state management."""
from enum import Enum, auto
from typing import Optional, Dict, Callable
import pygame

class GameState(Enum):
    """Game states."""
    MAIN_MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    HIGH_SCORE = auto()
    OPTIONS = auto()

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
        return cls._instance
        
    def __init__(self):
        """Initialize the state service."""
        if self._initialized:
            return
            
        self._current_state: Optional[GameState] = None
        self._previous_state: Optional[GameState] = None
        self._state_handlers: Dict[GameState, Callable] = {}
        
        # Set initial state
        self.change_state(GameState.MAIN_MENU)
        print("StateService initialized")
        self._initialized = True
        
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
                
            # Test handler call
            try:
                handler(0.0)  # Test with zero delta time
            except Exception as e:
                raise RuntimeError(f"Handler failed validation: {e}")
                
            self._state_handlers[state] = handler
            print(f"Registered handler for state {state.name}")
            
        except Exception as e:
            print(f"Error registering handler for state {state.name}: {e}")
            raise
        
    def change_state(self, new_state: GameState) -> None:
        """Change to a new game state.
        
        Args:
            new_state: State to change to
            
        Raises:
            ValueError: If new_state is invalid
            RuntimeError: If state transition fails
        """
        if not isinstance(new_state, GameState):
            raise ValueError(f"Invalid state type: {type(new_state)}")
            
        if new_state == self._current_state:
            return
            
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
            print(f"Changed state from {self._previous_state} to {new_state}")
            
            # Call enter handler for new state if it exists
            if new_state in self._state_handlers:
                handler = self._state_handlers[new_state]
                if hasattr(handler, 'on_enter'):
                    try:
                        handler.on_enter()
                    except Exception as e:
                        print(f"Error in enter handler for state {new_state.name}: {e}")
                        # Rollback state change
                        self._current_state = old_state
                        self._previous_state = old_previous
                        raise RuntimeError(f"Failed to enter state {new_state.name}: {e}")
                    
        except Exception as e:
            print(f"Error during state transition: {e}")
            # Ensure state is valid even if transition fails
            if self._current_state is None:
                print("Critical error: Reverting to MAIN_MENU")
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
        """Clean up the service."""
        self._current_state = None
        self._previous_state = None
        self._state_handlers.clear()
        print("StateService cleaned up") 